from bot import Educ
from OWM import OpenWeatherMap
from llm import DeepSeek
from utils import (save_offset, load_offset)
from json import(loads, dumps)
from urllib3 import (ProxyManager, make_headers)
from time import (sleep)
from dotenv import load_dotenv
from os import (getenv)


load_dotenv()

proxy_url = getenv("PROXY_URL")
proxy_user = getenv("PROXY_USER")
proxy_password = getenv("PROXY_PASSWORD")

auth_haders: dict = make_headers(
    proxy_basic_auth=f"{proxy_user}:{proxy_password}"
)

http: ProxyManager = ProxyManager(
    proxy_url=f"http://{proxy_url}",
    proxy_headers=auth_haders 
)


def main():
    owm_instance: OpenWeatherMap = OpenWeatherMap(request_manager=http)
    deep_srenk = DeepSeek(http)
    bot: Educ = Educ(
                    owm_instance=owm_instance,
                    llm=deep_srenk,
                    request_manager=http
                    )

    print(bot.offset)
    response = bot.get_updates()
    
    for request in response["result"]:
        message: dict = request.get("message")
        #todo: преписать лаконичнее
        is_command = False
        if message and "text" in message:
            entities = message.get("entities", [])
            for entity in entities:
                if entity.get("type") == "bot_command":
                    is_command = True
                    break

        if not is_command:
            chat_id = message["chat"]["id"]
            bot.send_message(chat_id, "Воспользуйтесь, командами бота")
        else:
            pass


           
        bot.save_offset(request["update_id"]+1)
        print(request)



    #

    #massage = deep_srenk.get_recomedation(weather)
    


    
    '''while True:
        

        
        
        try:
            pass

        except Exception as e:
            print("ERROR:", e)
            sleep(5)
'''
if __name__ == "__main__":
    main()


