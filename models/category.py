from db.dal_connect import get_dal_mysql
from schemas.category import CategoryModel


def get_all_categories():
    with get_dal_mysql() as db:
        categoriesDB = db().select(db.category.id).as_list()
    categories = list()
    for category in categoriesDB:
        categories.append(category["id"])
    return categories


def post_category(category: CategoryModel):
    with get_dal_mysql() as db:
        category = db(db.category.name==category.name).select().first()
        if category:
            raise Exception(detail="Esta categoria já existe")
        new = db.category.insert(**category.model_dump())
    return new


def check_category(categoryID):
    with get_dal_mysql() as db:
        category = db(db.category.id == categoryID).select(db.category.name).first()
    return True if category else False
