import os

from dotenv import load_dotenv
from pydal import DAL
from .tables import define_tables


USER = os.getenv("DBUSER")
PASSWORD = os.getenv("DBPASSWORD")
HOST = os.getenv("HOST", "localhost")
DATABASE = os.getenv("DATABASE")


class get_dal_mysql:
    """DAL class to abstract db connection"""

    def __init__(self):
        # mysql://user:pass@url/db
        uri = f"mysql://parking:parking@localhost/parking"

        driver_args = {}
        dal_conn = DAL(
            uri,
            pool_size=10,
            folder="./database",
            migrate=False,
            fake_migrate=True,
            fake_migrate_all=True,
            check_reserved=["all"],
            driver_args=driver_args,
        )
        define_tables(dal_conn)
        self.dal_conn = dal_conn
        self.dal_conn.database = DATABASE

    def __enter__(self, *args):
        return self.dal_conn

    def __exit__(self, *args):
        self.dal_conn.commit()
        self.dal_conn.close()