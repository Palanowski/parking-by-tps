from db.dal_connect import get_dal_mysql

def get_all_colors():
    with get_dal_mysql() as db:
        colors_from_db = db().select(db.color.id).as_list()
    colors = list()
    for color in colors_from_db:
        colors.append(color["id"])
    return colors


def update_or_insert_color(colorID):
    with get_dal_mysql() as db:
        color = db(db.color.id==colorID).select().first()
        if color:
            color.update(id=colorID)
        else:
            db.color.insert(id=colorID)
    return True


def delete_color(colorID):
    with get_dal_mysql() as db:
        color = db(db.color.id == colorID).select().first()
        if color:
            db(db.color.id == colorID).delete()
    return True