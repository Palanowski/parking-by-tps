from db.dal_connect import get_dal_mysql

def get_config():
    with get_dal_mysql() as db:
        config = db().select(db.config.ALL)
    return config.as_dict()[1]