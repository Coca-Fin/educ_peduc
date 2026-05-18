from os import getenv
from json import (dumps, loads)
from urllib3 import (ProxyManager, HTTPResponse)
from yaml import safe_load
from pathlib import Path
from typing import (Dict)


class DeepSeek():
    """

    args:
        request_manager: urllib3 ProxyManager or PoolManager
    """

    def __init__(self, request_manager):
        self.__token = getenv("DS_TOKEN")
        self.url: str = f"{getenv("DS_URL")}/"
        self.http: ProxyManager = request_manager
        self.payload: dict = {}
        self.data: dict = {}

    def get_recomedation(self, data: Dict) -> Dict:
        response = self.__api_request(data=self.__create_payload(self.__create_massages(data)))
        return loads(response)
    
    def __api_request(self, data={}) -> HTTPResponse:
        headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.__token}'
            }
        response: HTTPResponse = self.http.request(
            "POST",
            self.url,
            body=dumps(data).encode('utf-8'),
            headers=headers
        )
        return response
    
    def __create_payload(self, massages) -> dict:
        self.payload = {
                        "model": getenv("DS_MODEL"),
                        "messages": massages
        }
        return self.payload
    
    def __create_massages(self, data) -> list:
        current_dir = Path(__file__).parent
        file_path = current_dir / getenv("PROMPT_PATH")

        with open(file_path, "r", encoding="utf-8") as file:
            prompts = safe_load(file)
        
        massages = [
            {
                "role":"system",
                "content":prompts["system"]["content"]
            },
            {
                "role":"user",
                "content":f"{prompts['user']['content']}\n{dumps(data, ensure_ascii=False, indent=2)}"
            }
        ]
    
        return massages
    

        
    