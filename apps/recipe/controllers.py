
from yatl.helpers import A

from py4web import URL, abort, action, redirect, request, Field
from py4web.core import Template
from py4web.utils.form import Form

from yatl.helpers import DIV, LABEL, INPUT, SPAN

from .common import (
    T,
    auth,
    authenticated,
    cache,
    db,
    flash,
    logger,
    session,
    unauthenticated,
)

import re

from py4web import action, request, abort, redirect
from .common import auth

from pydal.validators import IS_IN_DB, IS_LIST_OF, IS_INT_IN_RANGE

# checkbox widget because py4web's built-in widget doesnt work for some reason
def make_checkbox_widget(field_name, options):
    """
    Returns a widget callback that renders check-boxes for the list field
    `field_name`.  `options` is a list of (id, label) tuples.
    """
    def _widget(_field, value, **attrs):
        # normalise selected values
        if isinstance(value, (list, tuple)):
            selected = {str(v) for v in value}
        elif value is not None:
            selected = {str(value)}
        else:
            selected = set()

        boxes = [
            LABEL(
                INPUT(
                    _type="checkbox",
                    _name=field_name,   # ← list input
                    _value=str(opt_id),
                    _checked=str(opt_id) in selected,
                ),
                SPAN(f" {label}"),
                _style="display:block; margin-bottom:4px;",
            )
            for opt_id, label in options
        ]
        return DIV(*boxes)
    return _widget


# helper calorie function
def _update_total_calories(recipe_id):
    total = 0
    for link in db(db.link.recipe_id == recipe_id).select():
        ing = db.ingredients[link.ingredient_id]
        total += link.quantity_per_serving * ing.calories_per_unit
    db.recipes[recipe_id] = dict(total_calories=total)

@action("index")
@action("/")
@action.uses("index.html", auth.user, T)
def index():
    user = auth.get_user()
    ingredients_form = Form(
        db.ingredients,
        fields=["name", "unit", "calories_per_unit", "description"],
        dbio=False
    )
    # Recipe form without allowing author field to be editable
    options = [(row.id, row.name) for row in db(db.ingredients).select()]

    ing_ids_field = Field(
        "ingredient_ids", "list:integer",
        label="Ingredients",
        requires=IS_IN_DB(db, "ingredients.id", "%(name)s", multiple=True),
        widget=make_checkbox_widget("ingredient_ids", options),
    )
    
    qtys_field = Field(
        "ingredient_qtys",
        "list:integer",
        label="Qty / serving (match order)",
        requires=IS_LIST_OF(IS_INT_IN_RANGE(1, 10000)),
    )

    recipe_fields = [
        db.recipes.name,
        db.recipes.type,
        db.recipes.description,
        db.recipes.image,
        db.recipes.instruction_steps,
        db.recipes.servings,
        ing_ids_field,
        qtys_field,
    ]
    recipes_form = Form(recipe_fields, dbio=False)
    
    if ingredients_form.accepted:
        print("Inserting ingredients:", ingredients_form.vars["name"])
        db.ingredients.insert(
            name=ingredients_form.vars["name"],
            unit=ingredients_form.vars["unit"],
            calories_per_unit=ingredients_form.vars["calories_per_unit"],
            description=ingredients_form.vars["description"],
        )
        redirect(URL("index"))
    
    if recipes_form.accepted:
        # 1) base recipe row
        rid = db.recipes.insert(
            name=recipes_form.vars["name"],
            type=recipes_form.vars["type"],
            description=recipes_form.vars["description"],
            image=recipes_form.vars["image"],
            instruction_steps=recipes_form.vars["instruction_steps"],
            servings=recipes_form.vars["servings"],
            author=user["id"],
        )

        # 2) normalise incoming values ────────────────────────────
        ing_ids = request.forms.getall("ingredient_ids")  # ← NEW
        raw_qty = recipes_form.vars.get("ingredient_qtys") or []

        # helper to split qtys the same way as before
        def to_list(val):
            if isinstance(val, (list, tuple)):
                return list(val)
            if isinstance(val, str):
                val = val.strip().lstrip("[").rstrip("]")
                return [v for v in re.split(r"[\s,]+", val) if v]
            return []

        qtys = to_list(raw_qty)

        # cast to int, keep only matching pairs
        pairs = [
            (int(i), int(q))
            for i, q in zip(ing_ids, qtys)
            if str(i).isdigit() and str(q).isdigit()
        ]

        # 3) insert link rows
        for ing_id, qty in pairs:
            db.link.insert(
                recipe_id=rid,
                ingredient_id=ing_id,
                quantity_per_serving=qty,
            )

        # 4) calories (only if at least one link)
        if pairs:
            _update_total_calories(rid)

        redirect(URL("index"))
    return {"user": user, "ingredients_form": ingredients_form, "recipes_form": recipes_form}

@action("/recipe/api/recipes",method=["GET"])
@action.uses(db)
def add_recipe():
    # returns all recipes in the database
    rows = db(db.recipes).select().as_list()
    print("returning recipes: ", rows)
    return {"recipes": rows}

@action("/recipe/api/ingredients",method=["GET"])
@action.uses(db)
def add_ingredients():
    # returns all recipes in the database
    rows = db(db.ingredients).select().as_list()
    print("returning ingredients: ", rows)
    return {"ingredients": rows}

@action("recipe/<rid:int>/edit", method=["GET", "POST"])
@action("<rid:int>/edit",        method=["GET", "POST"])
@action.uses("index.html", auth.user, T)        # reuse your main template
def recipe_edit(rid):
    user = auth.get_user()
    rec = db.recipes[rid] or abort(404)
    if rec.author != user["id"]:
        abort(403)          # NOT your recipe → 403 Forbidden

    # Grab current ingredient links to build defaults
    cur_links = db(db.link.recipe_id == rid).select()
    default_ids  = [l.ingredient_id for l in cur_links]
    default_qtys = [l.quantity_per_serving for l in cur_links]

    # Same two virtual fields as in index()
    options = [(row.id, row.name) for row in db(db.ingredients).select()]

    ing_ids_field = Field(
        "ingredient_ids", "list:integer",
        label="Ingredients",
        requires=IS_IN_DB(db, "ingredients.id", "%(name)s", multiple=True),
        widget=make_checkbox_widget("ingredient_ids", options),
    )
    
    qtys_field = Field(
        "ingredient_qtys", "list:integer",
        default=default_qtys,
        label="Qty / serving (match order)",
        requires=IS_LIST_OF(IS_INT_IN_RANGE(1, 10000)),
    )

    form = Form(
        [
            db.recipes.name,
            db.recipes.type,
            db.recipes.description,
            db.recipes.image,
            db.recipes.instruction_steps,
            db.recipes.servings,
            ing_ids_field,
            qtys_field,
        ],
        record=rec,
        deletable=False,
    )

    if form.accepted:
        # 1) update the core recipe fields
        db.recipes[rid] = form.vars

        # 2) rebuild the link table ----------------------------
        db(db.link.recipe_id == rid).delete()

        # NEW: get the checked boxes exactly as the browser sent them
        ing_ids = request.forms.getall("ingredient_ids")      # <- list of ids
        qtys    = form.vars.get("ingredient_qtys") or []      # stays the same

        # helper to be safe if qtys came back as a comma string
        def to_list(val):
            if isinstance(val, (list, tuple)):
                return list(val)
            if isinstance(val, str):
                val = val.strip().lstrip("[").rstrip("]")
                return [v for v in re.split(r"[\s,]+", val) if v]
            return []

        qtys = to_list(qtys)

        for ing_id, qty in zip(ing_ids, qtys):
            if str(ing_id).isdigit() and str(qty).isdigit():
                db.link.insert(
                    recipe_id=rid,
                    ingredient_id=int(ing_id),
                    quantity_per_serving=int(qty),
                )

        # 3) recompute calories
        _update_total_calories(rid)
        redirect(URL("index"))

    return {
        "user": user,
        "ingredients_form": None,   # hide ingredient form on this page
        "recipes_form": form,       # template shows this automatically
    }
    
@action("/recipe/api/debug/links", method="GET")
@action.uses(db)
def debug_links():
    # Quick view: which ingredients are linked to which recipes?
    rows = db(db.link).select(
        db.link.recipe_id, db.link.ingredient_id, db.link.quantity_per_serving
    ).as_list()
    return dict(links=rows)