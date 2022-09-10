from create_db import DatBase
from config import database, user, password, host, port, name_database

if __name__ == "__main__":
    db = DatBase(database, user, password, host, port, name_database)
    db.create_db()
    db.create_tables()
    print("Setup database successfully")
