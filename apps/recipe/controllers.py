import json

from py4web import action, URL, abort, redirect, request
from py4web.utils.form import Form

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

# Home page – shows ingredient form + lists (Vue handles recipe form)
@action("index")
@action("/")
@action.uses("index.html", auth.user, T)
def index():
    user = auth.get_user()

    # form to add ingredients
    ing_form = Form(
        db.ingredients,
        fields=["name", "unit", "calories_per_unit", "description"],
        dbio=False,
    )

    if ing_form.accepted:
        db.ingredients.insert(
            name=ing_form.vars["name"],
            unit=ing_form.vars["unit"],
            calories_per_unit=ing_form.vars["calories_per_unit"],
            description=ing_form.vars["description"],
        )
        flash.set("Ingredient added")
        redirect(URL("index"))

    # send full ingredient + recipe lists for the Vue app
    ingredients = db(db.ingredients).select().as_list()
    recipes     = db(db.recipes).select().as_list()

    return dict(user=user,
                ingredients_form=ing_form,
                ingredients=ingredients,
                recipes=recipes)

# Read only
@action("api/ingredients", method=["GET"])
@action.uses(db)
def api_ingredients():
    return dict(ingredients=db(db.ingredients).select().as_list())

@action("api/recipes", method=["GET"])
@action.uses(db)
def api_recipes():
    return dict(recipes=db(db.recipes).select().as_list())

# create or update
@action("api/recipe", method=["POST", "PUT"])
@action.uses(db, auth.user)
def api_save_recipe():
    data = request.json or abort(400, "Missing JSON payload")

    # common fields
    recipe_fields = {k: data.get(k) for k in (
        "name", "type", "description",
        "instruction_steps", "servings"
    )}
    recipe_fields["author"] = auth.user_id   # enforce

    # create or update
    if request.method == "POST":
        rid = db.recipes.insert(**recipe_fields)
    else:
        rid = data.get("id") or abort(400, "Missing id for update")
        rec = db.recipes[rid] or abort(404)
        if rec.author != auth.user_id:
            abort(403, "Not your recipe")
        rec.update_record(**recipe_fields)
        db(db.link.recipe_id == rid).delete()   # wipe old links

    # link ingredients + calorie sum 
    total = 0
    for link in data.get("ingredients", []):      # [{id, qty}, …]
        ing = db.ingredients[link["id"]] or abort(400, "Bad ingredient")
        qty = int(link["qty"])
        db.link.insert(recipe_id=rid,
                       ingredient_id=ing.id,
                       quantity_per_serving=qty)
        total += qty * ing.calories_per_unit

    total *= int(recipe_fields["servings"])
    db.recipes[rid].update_record(total_calories=total)

    return dict(status="ok", recipe_id=rid, total_calories=total)