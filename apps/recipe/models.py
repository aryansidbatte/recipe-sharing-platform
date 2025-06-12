from py4web import URL
from pydal.validators import *
from .common import Field, db, auth, settings

db.define_table(
    "ingredients",
    # If we don't want duplicates we can add unique=True to name
    Field("name", type="string", requires=IS_NOT_EMPTY()),
    Field("unit", type="integer", requires=IS_INT_IN_RANGE(0,1000)),
    Field("calories_per_unit", type="integer", requires=IS_INT_IN_RANGE(0,1000)),
    Field("description", type="text", requires=IS_NOT_EMPTY()),
)

db.define_table(
    "recipes",
    Field("name", "string", requires=IS_NOT_EMPTY()),
    Field("type", "string", requires=IS_NOT_EMPTY()),
    Field("description", "text"),
    Field("image", "upload",
          upload_path=settings.UPLOAD_FOLDER,
          download_url=lambda f: URL("download", f)),
    Field("instruction_steps", "text"),
    Field("servings", "integer", requires=IS_INT_IN_RANGE(1, 1000)),
    Field("total_calories", "integer", default=0, readable=True, writable=False),
    Field("author", "reference auth_user",
          readable=False, writable=False, default=lambda: auth.user_id),
    migrate=True,
)

db.define_table(
    "link",
    Field("recipe_id", "reference recipes", requires=IS_NOT_EMPTY()),
    Field("ingredient_id", "reference ingredients", requires=IS_NOT_EMPTY()),
    Field("quantity_per_serving", type="integer", requires=IS_INT_IN_RANGE(0,1000)),
)

db.commit()

# for table in db.tables:
#     db[table].drop()
# db.commit()