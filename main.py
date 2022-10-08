import json

import psycopg2

import bot_file
import logging

logger = logging.getLogger("SteamBot")
logger.setLevel(logging.INFO)

# create the logging file handler
fh = logging.FileHandler("logger.log", "w")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add handler to logger object
logger.addHandler(fh)


def main_func():
    logger.info("Program started")

    try:
        with open("config_db.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        psycopg2.connect(
            host=data['host'],
            user=data['user'],
            password=data['password'],
            database=data['db_name']
        )

        logger.info("Valid data for the database")
    except:

        print("Некорректные данные для подлкючения к бд!\nВвод новых данных:")
        logger.exception("Incorrect data for connecting to the database! Entering new data")

        print("host: ", end="")
        data['host'] = input()

        print("user: ", end="")
        data['user'] = input()

        print("password: ", end="")
        data['password'] = input()

        print("db_name: ", end="")
        data['db_name'] = input()

        with open("config_db.json", "w", encoding="utf-8") as file:
            json.dump(data, file)

        main_func()

    else:

        print("Успешное подлкючение к БД")
        print("Запуск бота...")
        logger.info("Successful connection to the database")
        logger.info("Bot started")

        bot_file.start_process_bot()


if __name__ == "__main__":
    main_func()
