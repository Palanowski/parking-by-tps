from db.dal_connect import get_dal_mysql
from schemas.category import CategoryModel


def get_all_categories():
    with get_dal_mysql() as db:
        categoriesDB = db().select(db.category.id).as_list()
    categories = list()
    for category in categoriesDB:
        categories.append(category["id"])
    return categories


def update_or_insert_category(categoryModel: CategoryModel):
    with get_dal_mysql() as db:
        category = db(db.category.id==category.id).select().first()
        if category:
            category.update(**categoryModel.model_dump(exclude_unset=True))
        else:
            db.category.insert(**categoryModel.model_dump(exclude_unset=True))
    return True


def check_category(categoryID):
    with get_dal_mysql() as db:
        category = db(db.category.id == categoryID).select().first()
    return True if category else False


def delete_category(categoryID):
    with get_dal_mysql() as db:
        category = db(db.category.id == categoryID).select().first()
        if category:
            db(db.category.id == categoryID).delete()
    return True
