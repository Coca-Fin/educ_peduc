from bot import Educ
from json import(loads)
from urllib3 import ProxyManager
from time import sleep
from dotenv import load_dotenv
from os import (getenv)


load_dotenv()


tg_token = getenv("TG_TOKEN")
proxy_url = getenv("PROXY_URL")
proxy_user = getenv("PROXY_USER")
proxy_password = getenv("PROXY_PASSWORD")

http: ProxyManager = ProxyManager(
    f"http://{proxy_user}:{proxy_password}@{proxy_url}"
)


def main():

    bot = Educ(token=tg_token, request_manager=http)
    
    while True:
        


        
        
        try:
            pass

        except Exception as e:
            print("ERROR:", e)
            sleep(5)

if __name__ == "__main__":
    print(
        f"""tg_token = {tg_token}
            proxy_url = {proxy_url}
            proxy_user = {proxy_user}
            proxy_password = {proxy_password}
        """
    )
    
    #main()
    bot = Educ(token=tg_token, request_manager=http)
    print(bot.get_me().readlines())


