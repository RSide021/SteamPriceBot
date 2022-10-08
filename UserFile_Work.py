import csv
import logging

module_logger = logging.getLogger("SteamBot.UserFile_Work")


def work_with_csv(id_user_sender):
    logger = logging.getLogger("SteamBot.UserFile_Work.Work_With_CSV")

    try:
        file_path = rf'tempUserData\{id_user_sender}.csv'
        with open(file_path, encoding='utf-8') as r_file:
            # Создаем объект DictReader, указываем символ-разделитель ","
            file_reader = csv.DictReader(r_file, delimiter=",")
            # Создаем список предметов в файле
            list_items = []
            # Считывание данных из CSV файла
            for row in file_reader:
                try:
                    list_items.append(url_string_parse(row['Url']))
                except Exception as _ex:
                    print(f'Column {_ex} not found')
            logger.info("File processes succesfully")
            return list_items
    except Exception as _ex:
        print(f"Error: {_ex}")
        logger.exception(f"File not processed: ")
        return []


def url_string_parse(url):
    logger = logging.getLogger("SteamBot.UserFile_Work.URL_String_Parse")

    try:
        app_id = url.split('/')[5]
        name_item = url.split('/')[6]

        logger.info("String processed succesfully")

        return {
            "appId": app_id,
            "name_item": name_item
        }
    except Exception as _ex:
        print(f'Error in string parsing')
        logger.exception(f"String not processed: ")


