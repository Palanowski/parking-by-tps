from db.dal_connect import get_dal_mysql


def get_all_status():
    with get_dal_mysql() as db:
        statusDB = db().select(db.parking_status.id).as_list()
    status = list()
    for item in statusDB:
        status.append(item["id"])
    return status


def update_or_insert_status(statusID: str):
    with get_dal_mysql() as db:
        status = db(db.parking_status.id==statusID).select().first()
        if status:
            db(db.parking_status.id==statusID).update(id=statusID)
        else:
            db.parking_status.insert(id=statusID)
    return True


def get_status_by_id(statusID):
    with get_dal_mysql() as db:
        status = db(db.parking_status.id == statusID).select().first()
    return status if status else False


def delete_status(statusID):
    with get_dal_mysql() as db:
        status = db(db.parking_status.id == statusID).select().first()
        if status:
            db(db.parking_status.id == statusID).delete()
    return True
