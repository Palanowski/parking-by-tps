from datetime import datetime
from pydal import Field


def define_tables(db):
    db.define_table(
        "config",
        Field("id", "integer", notnull=True),
        Field("tolerance", "integer", notnull=True),
        Field("printer_header", "string", length=256, notnull=True),
        Field("printer_footer", "string", length=256, notnull=True),
        primarykey=["id"],
    )

    db.define_table(
        "color",
        Field("id", "string", length=45, notnull=True),
        Field("created", "datetime", default=lambda: datetime.now()),
        Field("updated", "datetime", default=lambda: datetime.now()),
        primarykey=["id"],
    )

    db.define_table(
        "category",
        Field("id", "string", length=45, notnull=True),
        Field("price", "double", notnull=True),
        Field("daily_price", "integer", notnull=True),
        Field("created", "datetime", default=lambda: datetime.now()),
        Field("updated", "datetime", default=lambda: datetime.now()),
        primarykey=["id"],
    )

    db.define_table(
        "model",
        Field("id", "string", length=45, notnull=True),
        Field("category", "reference category.id"),
        Field("created", "datetime", default=lambda: datetime.now()),
        Field("updated", "datetime", default=lambda: datetime.now()),
        primarykey=["id"],
    )

    db.define_table(
        "parking_status",
        Field("id", "string", length=45, notnull=True),
        Field("created", "datetime", default=lambda: datetime.now()),
        Field("updated", "datetime", default=lambda: datetime.now()),
        primarykey=["id"],
    )

    db.define_table(
        "users",
        Field("name", "string", length=45, notnull=True),
        Field("password", "string", length=45, notnull=True),
        Field("role", "string", length=45, notnull=True),
        Field("ISactive", "boolean", default=True),
        Field("created", "datetime", default=lambda: datetime.now()),
        Field("updated", "datetime", default=lambda: datetime.now()),
        primarykey=["name"],
    )

    db.define_table(
        "parking",
        Field("id", "integer", notnull=True),
        Field("plate", "string", length=10, notnull=True),
        Field("barcode", "string", length=45, notnull=True),
        Field("model", "reference model.id"),
        Field("category", "reference category.id"),
        Field("color", "reference color.id"),
        Field("entry_date", "date", default=lambda: datetime.now().date()),
        Field("entry_time", "time", default=lambda: datetime.now().time()),
        Field("exit_time", "time"),
        Field("delta_time", "time"),
        Field("status", "reference parking_status.id", default="EM ABERTO"),
        Field("entry_user", "reference users.name"),
        Field("exit_user", "reference users.name"),
        Field("total_value", "double", default=None),
        Field("ISreturn", "boolean", default=False),
        Field("partialPayment", "double"),
        Field("addition", "double", default=None),
        Field("discount", "double", default=None),
        Field("byPlate", "boolean", default=False),
        Field("byCash", "boolean", default=False),
        primarykey=["id"],
    )

    db.define_table(
        "log_in",
        Field("id", "integer", notnull=True),
        Field("userID", "reference users.name"),
        Field("login_date", "datetime", default=lambda: datetime.now()),
        Field("logout_date", "datetime", default=None),
        primarykey=["id"],
    )