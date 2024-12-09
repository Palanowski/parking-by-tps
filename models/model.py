from db.dal_connect import get_dal_mysql
from schemas.model import ModelModel


def get_all_models():
    with get_dal_mysql() as db:
        modelsDB = db().select(db.model.id).as_list()
    models = list()
    for model in modelsDB:
        models.append(model["id"])
    return models


def post_model(modelModel: ModelModel):
    with get_dal_mysql() as db:
        model = db(db.model.id==modelModel.id).select().first()
        if model:
            raise Exception(detail="Este modelo já existe")
        new = db.model.insert(**modelModel.model_dump())
    return new


def check_model(modelID):
    with get_dal_mysql() as db:
        model = db(db.model.id == modelID).select().first()
    return model if model else False
