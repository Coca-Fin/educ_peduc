from OWM import OpenWeatherMap
from llm import DeepSeek
from utils import (save_offset, load_offset)
from os import getenv
from json import loads
from urllib3 import (ProxyManager, HTTPResponse)
from os.path import dirname, join
from yaml import safe_load, safe_dump


class Educ():
    """
    args:
        request_manager: urllib3 ProxyManager or PoolManager
    """
    
    def __init__(self, owm_instance, llm, request_manager):
        self.url: str = f"{getenv("TG_URL")}{getenv("TG_TOKEN")}/"
        self.offset = self.__load_offset()
        self.owm_instance: OpenWeatherMap = owm_instance
        self.llm: DeepSeek = llm
        self.http: ProxyManager = request_manager
        self.last_data: dict = {}

    def get_updates(self) -> dict:
        response = self.__api_request("getUpdates", {
            "timeout": 15,
            "offset": self.offset
        })
        data = loads(response.data)
        self.last_data = data
        return data

    def send_message(self, chat_id, text) -> None:
        self.__api_request("sendMessage", {
            "chat_id": chat_id,
            "text": text
        })
    
    def get_me(self) -> dict:
        response = self.__api_request("getMe", {
            "timeout": 15,
            "offset": self.offset
        })
        return loads(response)
    
    def ask_city(self, user_id, chat_id):
        """
        Запрашивает у пользователя город, ожидает его ввода,
        сохраняет через __save_user_city() и отправляет подтверждение.
        """
        self.send_message(chat_id, "Введите ваш город:")

        while True:
            updates = self.get_updates()
            if not updates.get("ok"):
                continue

            for upd in updates["result"]:
                message = upd.get("message") or {}
                if message.get("chat", {}).get("id") != chat_id:
                    continue                    # игнорируем сообщения не от этого пользователя
                if "text" not in message:
                    self.send_message(chat_id, "Город должен быть текстовым сообщением. Попробуйте ещё раз.")
                    break                       # заново запрашиваем обновления
                city = message["text"].strip()
                if not city:
                    self.send_message(chat_id, "Название города не может быть пустым. Введите ещё раз:")
                    break

                self.__save_user_city(user_id, city)
                self.send_message(chat_id, f"Город «{city}» сохранён.")
                return 
    
    def get_weather_rec(self, user_id: str):
        

        city = self.__load_user_city(user_id)

        if city is None:
            city = self.ask_city()
            self.__save_user_city(user_id=user_id, city=city)

        params = {
                "cnt":"9",
                "q":city,
                "appid":"",
                "units":"metric",
                "lang":"ru"
            }
        
        weather = self.owm_instance.get_data(params=params)
        massage = self.llm.get_recomedation(weather)
        return massage

    def save_offset(offset):
        path = join(dirname(__file__), ".offset")
        with open(path, "w") as f:
            f.write(str(offset))
    
    def save_user_data(self, data) -> None:
        pass

    def __api_request(self, method, data=None) -> HTTPResponse:
        response: HTTPResponse = self.http.request(
            "POST",
            self.url+method,
            fields=data or {}
        )
        return response

    def __save_user_city(user_id: int, city: str) -> None:
        path = join(dirname(__file__), "users.yaml")
        try:
            with open(path, "r") as f:
                data = safe_load(f) or {}
        except FileNotFoundError:
            data = {}
        data[user_id] = city
        with open(path, "w") as f:
            safe_dump(data, f)

    def __load_user_city(user_id: int):
        path = join(dirname(__file__), "users.yaml")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = safe_load(f)
            if data and user_id in data:
                return data[user_id]
            return None
        except FileNotFoundError:
            return None

    def __load_offset() -> int:
        path = join(dirname(__file__), ".offset")
        try:
            with open(path, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError) as e :
            print(f"Educ.__load_offset ERROR: {e}")
            return 0



#commands = {"/start": Educ.get_weather}
