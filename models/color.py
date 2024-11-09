from db.dal_connect import get_dal_mysql

def get_colors():
    with get_dal_mysql() as db:
        colors_from_db = db().select(db.color.id).as_list()
    colors = list()
    for color in colors_from_db:
        colors.append(color["id"])
    return colors