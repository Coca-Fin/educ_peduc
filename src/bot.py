from json import loads
from urllib3 import HTTPResponse

OFFSET = 0

class Educ():
    
    def __init__(self, token, request_manager):
        self.url = f"http://api.telegram.org/bot{token}/"
        self.http = request_manager
       #self.last_data=self.get_updates()


    def api_request(self, method, data=None) -> HTTPResponse:
        response: HTTPResponse = self.http.request(
            "POST",
            self.url+method,
            fields=data or {}
        )
        return response


    def get_updates(self):
        result = self.api_request("getUpdates", {
            "timeout": 15,
            "offset": OFFSET
        })
        return loads(result.data)


    def send_message(self, chat_id, text):
        self.api_request("sendMessage", {
            "chat_id": chat_id,
            "text": text
        })
    
    def get_me(self) -> HTTPResponse:
        result = self.api_request("getMe", {
            "timeout": 15,
            "offset": OFFSET
        })
        return result