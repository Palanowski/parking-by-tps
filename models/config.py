from db.dal_connect import get_dal_mysql

def get_config():
    with get_dal_mysql() as db:
        config = db().select(db.config.ALL)
    return config.as_dict()[1]


def update_config(tolerance: int = None, header: str = None, footer: str = None):
    with get_dal_mysql() as db:
        if tolerance:
            db(db.config.id==1).update(tolerance=tolerance)
        if header:
            db(db.config.id==1).update(printer_header=header)
        if footer:
            db(db.config.id==1).update(printer_footer=footer)
    return True