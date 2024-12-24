from datetime import datetime
from db.dal_connect import get_dal_mysql
from schemas.users import UsersModel


def get_all_users():
    with get_dal_mysql() as db:
        usersDB = db().select(db.users.name).as_list()
        if usersDB:
            return [user["name"] for user in usersDB]


def get_user_by_id(userID):
    with get_dal_mysql() as db:
        user = db(db.users.name == userID).select().first()
    return user.as_dict() if user else False


def update_or_insert_user(userModel: UsersModel):
    with get_dal_mysql() as db:
        user = db(db.users.id==userModel.id).select().first()
        if user:
            new_user = user.update(**userModel.model_dump(exclude_unset=True))
        else:
            new_user = db.users.insert(**userModel.model_dump(exclude_unset=True))
    return new_user


def delete_user(userID):
    with get_dal_mysql() as db:
        user = db(db.users.id==userID).select().first()
        if user:
            db(db.users.id==userID).delete()
    return True

def log_in(userID):
    with get_dal_mysql() as db:
        db.log_in.insert(userID=userID)


def log_out(userID):
    with get_dal_mysql() as db:
        db(db.log_in.userID==userID).update(log_out=datetime.now())