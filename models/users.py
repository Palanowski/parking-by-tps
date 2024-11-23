from datetime import datetime
from db.dal_connect import get_dal_mysql


def get_all_users():
    with get_dal_mysql() as db:
        usersDB = db().select(db.users.name).as_list()
        if usersDB:
            return [user["name"] for user in usersDB]


def get_user_by_id(userID):
    with get_dal_mysql() as db:
        user = db(db.users.name == userID).select().first()
    return user.as_dict() if user else False


def log_in(userID):
    with get_dal_mysql() as db:
        db.log_in.insert(userID=userID)


def log_out(userID):
    with get_dal_mysql() as db:
        db(db.log_in.userID==userID).update(log_out=datetime.now())