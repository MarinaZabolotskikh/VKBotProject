import json
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import token_club, id_club, token_api
from vk import UsersVk
from db import Userbot, Usersearch, Electlist, Blacklist, Photo, Like, Templist, Lastfind
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import database, user, password, host, port, name_database
from sqlalchemy import create_engine, delete

class Server:

    """
    Класс для отлова сообщений группы в VK и выполнения запрашивыемых команд
    """

    def __init__(self, token, id_club):
        self.token = token
        self.id_club = id_club
        self.token_api = token_api
        self.s = self.run_database()           #запуск соединения с бд при инициализации класса

    def listen_server(self, longpoll):            #отлов сообщений в чатах ВК
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["from_id"] != self.id_club:
                id = event.obj.message["from_id"]
                peer_id = event.obj.message["peer_id"]
                user_cmd = event.obj.message["text"].lower().strip()
                if user_cmd == "!help":                                             #Не красиво, но при вызове фукций через словарь методом get было дублирование выполнения команд (возможно не связано)
                    print (user_cmd)
                    self.get_help(vk_session, peer_id)
                if user_cmd == "!find":
                    print (user_cmd)
                    self.get_find(vk_session, id, peer_id)
                if user_cmd == "!elect":
                    print (user_cmd)
                    self.add_electlist(vk_session, id, peer_id)
                if user_cmd == "!electlist":
                    print (user_cmd)
                    self.show_electlist(vk_session, id, peer_id)
                if user_cmd == "!stop":
                    print (user_cmd)
                    return print("stop")

    def run_database(self):                                #запуск соединения с бд
        engine = create_engine(f"postgresql://{user}:{password}@{host}/{name_database}")
        Base = declarative_base()
        session = sessionmaker(bind=engine)
        s = session()
        return s

    def get_help(self, vk_session, peer_id):
        msg = """
            !help - список доступных команд
            !find - поиск
            !elect - Поместить в избранное человека из последнего запроса
            !electlist - Список избранных
            !ban - В черный список (не фукциональна)
            !banlist - Черный список (не фукциональна)
            !like - Поставить лайк (не фукциональна)
            !unlike - Убрать лайк (не фукциональна)
            """
        return vk_session.method("messages.send", {"peer_id": peer_id, "message": msg, "random_id": 0})

    def get_find(self, vk_session, id, peer_id):
        user_1 = UsersVk(self.token_api)                                                              #Инициализация класса пля получения данных через VkApi
        if self.s.query(Templist.id_user_tl).filter(Templist.id_user == id).first() == None:             #проверка пользователя на наличие данных в бд, если пусто первый запрос
            test = user_1.test_users(id)                                                                   #проверка пользователя на закрытость станицы
            if test == False:
                return vk_session.method("messages.send", {"peer_id": peer_id, "message": "Поиск для пользователя с закрытой страницей недоступен.", "random_id": 0})
            users = UsersVk.filter_users(user_1.seach_users(*UsersVk.seach_by_parameters(user_1.get_info_users(id))))                 #получение всех подходящих людей и сохранение данных и связей в бд формируется если данных нет в бд
            if self.s.query(Userbot).filter(Userbot.id_user == id).first() == None:
                us_b_d = Userbot(id_user=id)
                self.s.add(us_b_d)
                self.s.commit()
            for user in users:
                us_b_f = Usersearch(id_user=user["id"])
                us_tl = Templist(id_user=id, id_user_tl=user["id"])
                self.s.add_all([us_b_f, us_tl])
                self.s.commit()
        data = self.s.query(Templist.id_user_tl, Templist.id_templist).filter(Templist.id_user == id).first()        #выдача первой попавшейся связи в бд и ее сохранение в переменную
        us_tl = self.s.query(Templist).get(data[1])                                                                  #удаление этой связи из бд
        self.s.delete(us_tl)
        if self.s.query(Templist.id_user_tl).filter(Templist.id_user_tl == data[0]).first() == None:                   #проверка связей у других пользователей и дальнейшее удаление из бд при их отсутствии
            us_b_f = self.s.query(Usersearch).get(data[0])
            self.s.delete(us_b_f)
            self.s.commit()
        us_dict = user_1.get_info_users(data[0])                                                                      #формирование ответа на запрос в чат
        us_ph = user_1.get_photo_users(data[0])
        msg = f'''{us_dict["Name"]} {us_dict["Last_name"]}\nСсылка на профиль: https://vk.com/id{data[0]}\n'''
        answer = self.get_attachment(us_ph, data, peer_id, msg)
        if self.s.query(Lastfind.id_user).filter(Lastfind.id_user == id).first() == None:
            us_lf = Lastfind(id_user=id, id_user_lf=data[0])
            self.s.add(us_lf)
            self.s.commit()
        self.s.query(Lastfind).update({Lastfind.id_user:id, Lastfind.id_user_lf:data[0]})                                                         #сохранение последнего запроса в бд
        self.s.commit()
        return answer

    def add_electlist(self, vk_session, id, peer_id):
        if self.s.query(Lastfind).filter(Lastfind.id_user == id).first() == None:
            return vk_session.method("messages.send", {"peer_id": peer_id, "message": "Для начала воспользуйтесь поиском", "random_id": 0})
        data = self.s.query(Lastfind.id_user_lf, Lastfind.id_lf).filter(Lastfind.id_user == id).first()
        us_el = Electlist(id_user=id, id_user_el=data[0])
        self.s.add(us_el)
        self.s.commit()
        user_1 = UsersVk(self.token_api)
        us_dict = user_1.get_info_users(data[0])
        last_find = self.s.query(Lastfind).get(data[1])                                                     #сохранение последнего запроса в бд
        self.s.delete(last_find)
        self.s.commit()
        return vk_session.method("messages.send", {"peer_id": peer_id, "message": f"""Пользователь {us_dict["Name"]} {us_dict["Last_name"]} - Ссылка на профиль: https://vk.com/id{data[0]}\nсохранен с списке избранных""", "random_id": 0})

    def show_electlist(self, vk_session, id, peer_id):
        if self.s.query(Electlist).filter(Electlist.id_user == id).first() == None:
            return vk_session.method("messages.send", {"peer_id": peer_id, "message": "Список пуст", "random_id": 0})
        data = self.s.query(Electlist.id_user_el).filter(Electlist.id_user == id).all()
        msg = self.get_msg(data)
        return vk_session.method("messages.send", {"peer_id": peer_id, "message": msg, "random_id": 0})

    def get_msg(self, data):
        user_1 = UsersVk(self.token_api)
        for i, dt in enumerate(data):
            us_dict = user_1.get_info_users(dt)
            if i == 0:
                msg = f"""{i+1}. {us_dict["Name"]} {us_dict["Last_name"]} - Ссылка на профиль: https://vk.com/id{dt}"""
            else:
                msg = msg + f"""\n{i+1}. {us_dict["Name"]} {us_dict["Last_name"]} - Ссылка на профиль: https://vk.com/id{dt}"""
        return msg

    def get_attachment(self, us_ph, data, peer_id, msg):                 #костыль из-за недостаточного ко-ва фото на странице
        if len(us_ph) == 1:
            return vk_session.method("messages.send", {"peer_id": peer_id, "message": msg, "attachment": f'photo{data[0]}_{us_ph[0]}', "random_id": 0})
        if len(us_ph) == 2:
            return vk_session.method("messages.send", {"peer_id": peer_id, "message": msg, "attachment": f'photo{data[0]}_{us_ph[0]}', "random_id": 0}), vk_session.method("messages.send", {"peer_id": peer_id, "attachment": f'photo{data[0]}_{us_ph[1]}', "random_id": 0})
        if len(us_ph) == 3:
            return vk_session.method("messages.send", {"peer_id": peer_id, "message": msg, "attachment": f'photo{data[0]}_{us_ph[0]}', "random_id": 0}), vk_session.method("messages.send", {"peer_id": peer_id, "attachment": f'photo{data[0]}_{us_ph[1]}', "random_id": 0}), vk_session.method("messages.send", {"peer_id": peer_id, "attachment": f'photo{data[0]}_{us_ph[2]}', "random_id": 0})


if __name__ == '__main__':
    server = Server(token_club, id_club)
    vk_session = vk_api.VkApi(token=token_club)
    longpoll = VkBotLongPoll(vk_session, id_club)
    server.listen_server(longpoll)
