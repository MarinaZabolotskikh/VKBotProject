import vk_api
import requests
from datetime import date
from pprint import pprint
from config import token_api

class UsersVk:

    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()

    def test_users(self, user_id):                                   #проверка на закрытость страницы, поиска данных по городу может быть недостаточно, возможно падение скрипта
        info = self.vk.users.get(user_ids=user_id, fields="city, sex, bdate, interests, music, books, movies")
        res = info[0].get("city", False)
        return res

    def get_info_users(self, user_id):                                #инфо со страницы по id, самая важная фукция (не ломать)
        info = self.vk.users.get(user_ids=user_id, fields="city, sex, bdate, interests, music, books, movies")
        sex = info[0]["sex"]
        if info[0]["sex"] == 1:
            sex = "женский"
        elif info[0]["sex"] == 2:
            sex = "мужской"
        birth = info[0]["bdate"]
        if len(birth) > 4:
            year_birth = int(birth.split(".")[2])
            age = date.today().year - year_birth
        else:
            age = None
        user = {
            "id":user_id,
            "Name":info[0]["first_name"],
            "Last_name":info[0]["last_name"],
            "city":info[0]["city"]["title"],
            "city_id":info[0]["city"]["id"],
            "sex_id":info[0]["sex"],
            "sex":sex,
            "age":age,
        }
        return user

    @classmethod
    def seach_by_parameters(cls, info_user:dict):            #формирование данных для поиска
        city_users = info_user["city_id"]
        age_users = info_user["age"]
        if info_user["sex_id"] == 1:
            gender_users = 2
        elif info_user["sex_id"] == 2:
            gender_users = 1
        else:
            pass
        return [age_users, gender_users, city_users]

    @classmethod
    def filter_users(cls, list_users: list):               #фильтр фукция
        return [users for users in list_users if users["is_closed"] == False
                and "city" in users
                and "bdate" in users
                and len(users["bdate"].split('.')) > 2]

    def seach_users(self, age:int, sex:int, city:int):          #поиск людей противоположного пола по возрасту и городу (есть косяки в выдаче результатов от ВК по части города)
        info = self.vk.users.search(age_from=age, age_to=age, sex=sex, city=city,
                                    fields="city, sex, bdate, interests, music, books, movies", count=1000, has_photo=1)
        return self.filter_users(info["items"])

    def get_photo_users(self, user_id):                     #получение фото
        list_photo = self.vk.photos.get(owner_id=user_id, album_id="profile", extended=1)
        dict_photo = {}
        for photo in list_photo["items"]:
            dict_photo[photo["id"]] = photo["likes"]["count"]
        max_like = sorted(dict_photo.items(), reverse=True)[:3]
        return [id_photo[0] for id_photo in max_like]

    def save_data(self, res_list:list):         #формирование списка словарей по поиску людей (красиво, но медленная работа, не используется)
        list_of_users = []
        for user in res_list:
            photo = self.get_photo_users(user["id"])
            sex = user["sex"]
            if user["sex"] == 1:
                sex = "женский"
            elif user["sex"] == 2:
                sex = "мужской"
            birth = user["bdate"]
            year_birth = int(birth.split(".")[2])
            age = date.today().year - year_birth
            res_dict = {
                "Name": user["first_name"],
                "Last_name": user["last_name"],
                "city": user["city"]["title"],
                "city_id": user["city"]["id"],
                "sex_id": user["sex"],
                "sex": sex,
                "age": age,
                "interests": user.get("interests"),
                "favorite_movies": user.get("movies"),
                "favorite_music": user.get("music"),
                "favorite_books": user.get("books"),
                "photo": photo
            }
            list_of_users.append(res_dict)
        return list_of_users
