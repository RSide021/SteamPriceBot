import requests
import json
import logging

module_logger = logging.getLogger("SteamBot.Request_Price_Things")


def get_data_about_things(market_hash_name, appid):
    logger = logging.getLogger("SteamBot.Request_Price_Things.Get_Data_About_Thins")

    url = 'https://steamcommunity.com/market/priceoverview/' + \
          f'?appid={appid}&country=RU&currency=5&market_hash_name={market_hash_name}'
    response = requests.get(url)
    data = json.loads(response.text)
    if data['success']:
        logger.info("Data receive succefully")
        return data
    else:
        logger.exception("Data not received")
        return []
