from datetime import datetime
from pydal import Field


def define_tables(db):
    db.define_table(
        "config",
        Field("id", "integer", notnull=True),
        Field("tolerance", "integer", notnull=True),
        Field("daily_price_vehicle", "integer", notnull=True),
        Field("daily_price_moto", "integer", notnull=True),
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
        Field("id", "integer", notnull=True),
        Field("name", "string", length=45, notnull=True),
        Field("password", "string", length=45, notnull=True),
        Field("role", "string", length=45, notnull=True),
        primarykey=["name"],
    )

    db.define_table(
        "parking",
        Field("id", "integer", notnull=True),
        Field("plate", "string", length=10, notnull=True),
        Field("regNumber", "integer", notnull=True),
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
        Field("total_value", "double", notnull=True),
        Field("addition", "double", notnull=True),
        Field("discount", "double", notnull=True),
        primarykey=["id"],
    )
