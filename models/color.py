from db.dal_connect import get_dal_mysql
from schemas.color import ColorModel

def get_colors():
    with get_dal_mysql() as db:
        colors_from_db = db().select(db.color.id).as_list()
    colors = list()
    for color in colors_from_db:
        colors.append(color["id"])
    return colors


def post_color(colorModel: ColorModel):
    with get_dal_mysql() as db:
        color = db(db.color.id==color.id).select().first()
        if color:
            raise Exception(detail="Esta cor já existe")
        new = db.color.insert(**colorModel.model_dump())
    return new