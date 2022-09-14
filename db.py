import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, DateTime
from config import database, user, password, host, port, name_database

engine = create_engine(f"postgresql://{user}:{password}@{host}/{name_database}")  #генерация бд при проходе интерпритатора
Base = declarative_base()

class Userbot(Base):   #таблица юзеров бота
    __tablename__ = 'Userbot'
    id_user = Column(Integer, primary_key=True)

class Usersearch(Base):     #таблица с данными по запросам
    __tablename__ = 'Usersearch'
    id_user = Column(Integer, primary_key=True)

class Electlist(Base):           #таблица сохраненых избранных пользователей
    __tablename__ = 'Electlist'
    id_electlist = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("Userbot.id_user"))
    id_user_el = Column(Integer)
    Userbot = relationship("Userbot")

class Blacklist(Base):            #таблица сохраненых пользователей в ЧС
    __tablename__ = 'Blacklist'
    id_blacklist = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("Userbot.id_user"))
    id_user_bl = Column(Integer)
    Userbot = relationship("Userbot")

class Photo(Base):                #таблица не используется
    __tablename__ = 'Photo'
    id_photo = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("Usersearch.id_user"))
    link = Column(String(100))
    Usersearch = relationship("Usersearch")

class Like(Base):                  #таблица не используется
    __tablename__ = 'Likes'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("Userbot.id_user"))
    id_photo = Column(Integer, ForeignKey("Photo.id_photo"))
    Userbot = relationship("Userbot")
    Photo = relationship("Photo")

class Templist(Base):           #создание связи между пользователями запрос-ответ
    __tablename__ = 'Templist'
    id_templist = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("Userbot.id_user"))
    id_user_tl = Column(Integer, ForeignKey("Usersearch.id_user"))
    data_date = Column(DateTime(timezone=True), default=func.now())  #для чистки таблицы по таймингу (не реализовано)
    Userbot = relationship("Userbot")
    Usersearch = relationship("Usersearch")

class Lastfind(Base):           #создание связи между пользователями запрос-ответ
    __tablename__ = 'Lastfind'
    id_lf = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("Userbot.id_user"))
    id_user_lf = Column(Integer)
    data_date = Column(DateTime(timezone=True), default=func.now())  #для чистки таблицы по таймингу (не реализовано)
    Userbot = relationship("Userbot")


Base.metadata.create_all(engine)       #генерация бд при проходе интерпритатора
