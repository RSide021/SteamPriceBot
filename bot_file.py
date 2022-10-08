from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.dispatcher.filters import Text
from telegram_auth import token
import DB_Work
import UserFile_Work
from request_price_things import get_data_about_things
import logging
import os

bot = Bot(token=token)
dp = Dispatcher(bot)

module_logger = logging.getLogger("SteamBot.Bot_File")


@dp.message_handler(commands='start')
async def start(message: types.Message):
    logger = logging.getLogger("SteamBot.Bot_File.Start")

    try:
        start_buttons = ['Добавление данных', 'Очистка данных', 'Запрос цен', 'Список предметов']
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*start_buttons)
        text_msg = "Приветствую!\nДанный бот будет мониторить цены скинов на ТП Steam!"
        await message.answer(text_msg, reply_markup=keyboard)
        logger.info(f"Success - {message.from_id}")
    except Exception as ex:
        print(f"Проблема обработки сообщения [start]: {ex}")
        logger.exception(f"Error in: ")


@dp.message_handler(commands='add_data')
@dp.message_handler(Text(equals="Добавление данных"))
async def add_data_button(message: types.Message):
    logger = logging.getLogger("SteamBot.Bot_File.Add_Data_Button")

    try:
        text_msg = "Для создания списка отслеживаемых данных необходимо заполнить ниже прикпреленный файл и прислать его."
        await message.answer(text_msg)
        await message.answer_document(open("data.csv", 'rb'))
        logger.info(f"Success - {message.from_id}")
    except Exception as ex:
        print(f"Проблема обработки сообщения [add_data]: {ex}")
        logger.exception(f"Error in: ")


@dp.message_handler(commands='clear_data')
@dp.message_handler(Text(equals="Очистка данных"))
async def clear_db(message: types.Message):
    logger = logging.getLogger("SteamBot.Bot_File.Clear_DB")

    try:
        if DB_Work.clear_info_about_user(message.from_id):
            await message.answer("Данные успешно удалены")
            logger.info(f"Success - {message.from_id}")
        else:
            await message.answer("Ошибка очистки данных")
    except Exception as ex:
        print(f"Проблема обработки сообщения [clear_data]: {ex}")
        logger.exception(f"Error in: ")


@dp.message_handler(Text(equals="Запрос цен"))
@dp.message_handler(commands='get_prices')
async def get_prices(message: types.Message):
    logger = logging.getLogger("SteamBot.Bot_File.Get_Prices")

    try:
        list_items = DB_Work.get_all_things_users(message.from_id)
        for item in list_items:
            market_hash_name = item[0]
            app_id = item[1]
            price_data = get_data_about_things(market_hash_name, app_id)
            name_thing = format_hash_name(market_hash_name)
            if len(price_data):
                text = f"Предмет - <code>{name_thing}</code>\n" + \
                       f"Цена лота на продаже - <code>{price_data['lowest_price']}</code>\n" + \
                       f"Объем продаж за 24ч - <code>{price_data['volume']}</code>\n" + \
                       f"Средняя цена продажи за 24ч - <code>{price_data['median_price']}</code>\n" + \
                       md.hlink("Ссылка", f"https://steamcommunity.com/market/listings/{app_id}/{market_hash_name}")
                await message.answer(text, parse_mode="HTML")
            else:
                await message.answer(f"<code>{name_thing}</code>\nНе получилось получить цену предмета",
                                     parse_mode="HTML")
        logger.info(f"Success - {message.from_id}")
    except Exception as ex:
        print(f"Проблема обработки сообщения [get_prices]: {ex}")
        logger.exception(f"Error in: ")


@dp.message_handler(content_types='document')
async def get_file_from_user(message: types.Message):
    logger = logging.getLogger("SteamBot.Bot_File.Get_Prices")

    try:
        # Проверка формата файла
        if check_truth_file_type(message):
            await message.answer("Файл получен, начат процесс обработки!")
            logger.info("tThe file is valid")
        else:
            logger.exception("Invalid file")
            return await message.reply("Неверный тип файла")

        # Загрузка файла с данными
        await save_temp_file(message)

        telegram_id = message.from_id
        list_items = UserFile_Work.work_with_csv(telegram_id)

        # Удаление временных файлов
        file_path = rf'tempUserData\{telegram_id}.csv'
        if os.path.isfile(file_path):
            os.remove(file_path)


        if not len(list_items):
            logger.exception("Empty file")
            return await message.answer("Ошибка обработки данных!\nДанные пусты.")

        # Вставка новых строк в базу данных
        if DB_Work.insert_items_from_user(list_items, telegram_id):
            await message.answer("Обработка окончена! Данные успешно внесены в систему")
            logger.info(f"Success - {message.from_id}")
        else:
            await message.answer("Обработка окончена! Ошибка внесения данных в систему!")
    except Exception as ex:
        print(f"Проблема обработки сообщения [load_document]: {ex}")
        logger.exception(f"Error in: ")


@dp.message_handler(Text(equals="Список предметов"))
@dp.message_handler(commands='get_things')
async def get_prices(message: types.Message):
    logger = logging.getLogger("SteamBot.Bot_File.Get_Prices")

    try:
        list_items = DB_Work.get_all_things_users(message.from_id)
        buttons = []
        for item in list_items:
            market_hash_name = item[0]
            app_id = item[1]
            name_thing = format_hash_name(market_hash_name)
            buttons.append(
                types.InlineKeyboardButton(text=name_thing, callback_data=f"item_{market_hash_name}_{app_id}")
            )
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await message.answer("Список предметов:", reply_markup=keyboard)
        logger.info(f"Success - {message.from_id}")
    except Exception as ex:
        print(f"Проблема обработки сообщения [get_things]: {ex}")
        logger.exception(f"Error in: ")


@dp.callback_query_handler(Text(startswith="item_"))
async def callbacks(call: types.CallbackQuery):
    logger = logging.getLogger("SteamBot.Bot_File.CallBacks")

    try:
        market_hash_name = call.data.split('_')[1]
        app_id = call.data.split('_')[2]
        name_thing = format_hash_name(market_hash_name)
        price_data = get_data_about_things(market_hash_name, app_id)
        if len(price_data):
            text = f"Предмет - <code>{name_thing}</code>\n" + \
                   f"Цена лота на продаже - <code>{price_data['lowest_price']}</code>\n" + \
                   f"Объем продаж за 24ч - <code>{price_data['volume']}</code>\n" + \
                   f"Средняя цена продажи за 24ч - <code>{price_data['median_price']}</code>\n" + \
                   md.hlink("Ссылка", f"https://steamcommunity.com/market/listings/{app_id}/{market_hash_name}")
            await call.message.answer(text, parse_mode="HTML")
            logger.info(f"Success - {call.message.from_id}")
        else:
            await call.message.answer(f"<code>{name_thing}</code>\nНе получилось получить цену предмета",
                                      parse_mode="HTML")
        await call.answer()
    except Exception as ex:
        print(f"Проблема обработки сообщения [item_callback]: {ex}")
        logger.exception(f"Error in: ")


def check_truth_file_type(message):
    if message.document.mime_type == "text/csv":
        return True
    return False


async def save_temp_file(message):
    logger = logging.getLogger("SteamBot.Bot_File.Save_Temp_File")
    try:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, rf"tempUserData\{message.from_id}.csv")
        logger.info("The file has been downloaded successfully")
    except Exception as ex:
        print(f"Проблема загрузки файла - {ex}")
        logger.exception(f"Error in: ")


def format_hash_name(hash_name):
    return hash_name.replace('%20', ' ').replace('%7C', '|')


def start_process_bot():
    logger = logging.getLogger("SteamBot.Bot_File.StartProcess")
    logger.info("Checking the database")
    if DB_Work.connect_to_db():
        executor.start_polling(dp)


if __name__ == '__main__':
    start_process_bot()
