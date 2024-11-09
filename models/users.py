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