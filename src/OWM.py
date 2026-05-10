from os import getenv
from json import loads
from urllib3 import (ProxyManager, HTTPResponse, PoolManager)



class OpenWeatherMap():
    """

    args:
        request_manager: urllib3 ProxyManager or PoolManager
    """

    def __init__(self, request_manager):
        self.__appid: str = getenv("OWM_TOKEN")
        self.url: str = f"{getenv("OWM_URL")}/"
        self.http: ProxyManager = request_manager
        self.data :dict = {}

    def __api_request(self, method, data=None) -> HTTPResponse:
        response: HTTPResponse = self.http.request(
            "GET",
            self.url+method,
            fields=data or {}
        )
        return response
    
    def get_data(self, params:dict) -> dict:
        params["appid"] = self.__appid
        response = self.__api_request(method="forecast", 
                                            data=params)
        response = loads(response.data)
        return response
