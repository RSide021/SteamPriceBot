import json
import logging
import psycopg2

module_logger = logging.getLogger("SteamBot.DB_Work")


def connect_to_db():
    logger = logging.getLogger("SteamBot.DB_Work.Connect_To_DB")
    try:
        #  connect to exist database
        connection = create_connection_db()

        connection.autocommit = True

    except Exception as _ex:
        print("[INFO] Error while working with PosgreSQL", _ex)
        logger.exception(f"Error while working with PosgreSQL: ")
        return False
    else:
        connection.close()
        print("[INFO] PostgreSQL connection was successfully connected and closed")
        logger.info("PostgreSQL connection was successfully connected and closed")
        return True


def create_connection_db():
    logger = logging.getLogger("SteamBot.DB_Work.Create_Connection")

    with open("config_db.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    host = data['host']
    user = data['user']
    password = data['password']
    db_name = data['db_name']

    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )


def insert_items_from_user(list_items, telegram_id):
    logger = logging.getLogger("SteamBot.DB_Work.Insert_Items_From_User")

    try:
        #  connect to exist database
        connection = create_connection_db()
        connection.autocommit = True

        with connection.cursor() as cursor:
            for item in list_items:
                try:
                    cursor.execute("""
                    insert into public."Items" values (%s, %s, %s)""", (telegram_id, item['name_item'], item['appId']))
                except:
                    continue

    except Exception as _ex:
        if _ex.pgcode == "23505":
            connection.close()
            print("[INFO] SQL Query has already been executed")
            logger.info("SQL Query has already been executed")
            return True
        print("[INFO] Error while working with PosgreSQL", _ex)
        logger.exception(f"Error while working with PosgreSQL: ")
        return False
    else:
        connection.close()
        print("[INFO] SQL Query Insert completed successfully")
        logger.info("SQL Query has already been executed")
        return True


def clear_info_about_user(telegram_id):
    logger = logging.getLogger("SteamBot.DB_Work.Clear_Info_About_User")

    try:
        #  connect to exist database
        connection = create_connection_db()
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("""delete from public."Items" where "Items"."owner_id"= %s""", (f'{telegram_id}',))
    except Exception as _ex:
        print("[INFO] Error while working with PosgreSQL", _ex)
        logger.exception(f"Error while working with PosgreSQL: ")
        return False
    else:
        connection.close()
        print("[INFO] SQL Query Delete completed successfully")
        logger.info("SQL Query Delete completed successfully")
        return True


def get_all_things_users(telegram_id):
    logger = logging.getLogger("SteamBot.DB_Work.Get_All_Things_Users")

    try:
        #  connect to exist database
        connection = create_connection_db()
        connection.autocommit = True
        list_items = []
        with connection.cursor() as cursor:
            cursor.execute("""select "item_name", "appId" from public."Items" where "Items"."owner_id"= %s""",
                           (f"{telegram_id}",))
            list_items = cursor.fetchall()
    except Exception as _ex:
        print("[INFO] Error while working with PosgreSQL", _ex)
        logger.exception(f"Error while working with PosgreSQL: ")
        return list_items
    else:
        connection.close()
        print("[INFO] SQL-Query Select completed successfully")
        logger.info("SQL Query Select completed successfully")
        return list_items
