import psycopg2
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from config import database, user, password, host, port, name_database

class DatBase:


    def __init__(self, database, user, password, host, port, name_database):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.name_database = name_database

    def create_db(self):
        conn = psycopg2.connect(database=f"{self.database}", user=f"{self.user}", password=f"{self.password}", host=f"{self.host}", port= f"{self.port}")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f'''CREATE DATABASE {self.name_database}''')
        conn.close()
        return print("Database created successfully")

    def create_tables(self):
        meta = MetaData()
        users = Table("users", meta, Column("id_user", Integer, primary_key=True), Column("name", String(30)), Column("surname", String(40)), Column("age", Integer), Column("sex", String(10)), Column("sity", String(30)), Column("link", String(100)))
        electlist = Table("electlist", meta, Column("id_electlist", Integer, primary_key=True), Column("id_user", Integer, ForeignKey("users.id_user")), Column("id_user_el", Integer, ForeignKey("users.id_user")))
        blacklist = Table("blacklist", meta, Column("id_blacklist", Integer, primary_key=True), Column("id_user", Integer, ForeignKey("users.id_user")), Column("id_user_bl", Integer, ForeignKey("users.id_user")))
        photo = Table("photo", meta, Column("id", Integer, primary_key=True), Column("id_user", Integer, ForeignKey("users.id_user")), Column("id_photo", Integer, unique=True), Column("link", String(100)))
        likes = Table("likes", meta, Column("id", Integer, primary_key=True), Column("id_user", Integer, ForeignKey("users.id_user")), Column("id_photo", Integer, ForeignKey("photo.id_photo")))
        engine = create_engine(f"postgresql://{self.user}:{self.password}@{self.host}/{self.name_database}")
        meta.create_all(engine)
        return print("Tables created successfully")
