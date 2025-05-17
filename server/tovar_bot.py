import sqlite3
import asyncio

import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import FSInputFile
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
from config_tovar import BOT_TOKEN
from const import DEVS_ID

import aiohttp

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USERS_NAMES_ID = set()


class AddProductStates(StatesGroup):
    waiting_for_yandex_link = State()
    waiting_for_image_link = State()
    waiting_for_price = State()
    waiting_for_title = State()
    waiting_for_type_car = State()


conn = sqlite3.connect('cars.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS all_cars (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    image_link TEXT,
    price REAL,
    yandex_link TEXT,
    type_car TEXT
);
''')
conn.commit()

from car_mark import sercher


def search_car(user_input):
    user_input = sercher(user_input)
    if user_input is not None:
        cursor.execute(
            "SELECT title, image_link, price, yandex_link, type_car FROM all_cars WHERE LOWER(type_car) LIKE ?",
            ('%' + user_input.lower() + '%',))
        result = cursor.fetchone()
        if result:
            title, image_link, price, yandex_link, type_car = result
            answer_text = {'title': f'{title}',
                           'price': f"{price:.2f} руб.",
                           'image_url': f'{image_link}',
                           'link': f'{yandex_link}',
                           'type': f'{type_car}'}
            return answer_text
        else:
            return None
    else:
        return None


# Обработчик старта (/start и /help), выводящий приветствие и доступный список команд
@dp.message(Command('start'))
@dp.message(Command('help'))
async def start_tovars(message: types.Message):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    help_message = """
        Привет! Это бот для поиска машины по её марке.
        Доступные команды:
        /develop - показывает список всех комманд (только для разработчиков)
        /help or /start - выводит список комманд
        /list - список доступных марок
        Напиши название марки машины чтобы найти её!
        """

    button1 = types.InlineKeyboardButton(text="Завершить сеанс",
                                         callback_data="back")
    button2 = types.InlineKeyboardButton(text="Global-бот (ссылка)",
                                        url="t.me/MainCo6akaBot")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]])

    await message.answer(help_message, reply_markup=keyboard)


@dp.message(Command('get_url'))
async def get_url(message: types.Message):
    messages = "Вот кнопка для возвращения:"

    button1 = types.InlineKeyboardButton(text="Global-бот (ссылка)",
                                         url="t.me/MainCo6akaBot")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button1]])

    await message.answer(messages, reply_markup=keyboard)


@dp.callback_query(lambda call: call.data == 'back')
async def handle_back_button(call: types.CallbackQuery):
    await call.answer("Завершаем работу...")
    await get_url(call.message)
    await bot.session.close()
    await dp.stop_polling()


@dp.message(Command('develop'))
async def help_tovars_devs(message: types.Message):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    if message.from_user.id in DEVS_ID:
        help_message = """
        /add - добавить новый товар (только для разработчиов)
        /help or /start - выводит список комманд
        /list - выводит список всех доступных марок
        /develop - показывает список всех комманд (только для разработчиков)
        /add_dev - добавление нового временного разработчика
        /all_id - выводит список всех id и никноймов пользователей
        """
        await message.answer(help_message)
    else:
        await message.answer(
            "У вас недостаточно прав для выполнения данной команды.")


@dp.message(Command('list'))
async def add_new_product(message: types.Message, state: FSMContext):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    import car_mark
    res1 = "\n".join(car_mark.eng_marks)
    res2 = "\n".join(car_mark.ru_marks)
    res = res1 + "\n" + res2

    await message.answer(res)


# Обработчик команды /add_tovar
@dp.message(Command('add'))
async def add_new_product(message: types.Message, state: FSMContext):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    if message.from_user.id in DEVS_ID:
        await message.answer("Отправьте ссылку на авто:")
        await state.set_state(AddProductStates.waiting_for_yandex_link)
    else:
        await message.answer(
            "У вас недостаточно прав для выполнения данной команды.")


@dp.message(Command('add_dev'))
async def add_developer(message: types.Message, state: FSMContext):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    global DEVS_ID
    if message.from_user.id in DEVS_ID:
        await message.answer(
            "Введите ID пользователя, которого хотите добавить в разработчики:")
        DEVS_ID.add(message.from_user.id)
    else:
        await message.answer(
            "У вас недостаточно прав для выполнения данной команды.")


@dp.message(Command('all_id'))
async def add_developer(message: types.Message, state: FSMContext):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    global DEVS_ID
    if message.from_user.id in DEVS_ID:
        await message.answer(
            "Вот список всех id и никнеймов:")
        messages = f"{'\n'.join(list(map(str, USERS_NAMES_ID)))}"
        await message.answer(messages)
    else:
        await message.answer(
            "У вас недостаточно прав для выполнения данной команды.")


# Получаем ссылку на товар
@dp.message(AddProductStates.waiting_for_yandex_link)
async def receive_yandex_link(message: types.Message, state: FSMContext):
    yandex_link = message.text.strip()
    await state.update_data(yandex_link=yandex_link)
    await message.answer("Отправьте ссылку на фотографию товара:")
    await state.set_state(AddProductStates.waiting_for_image_link)


# Получаем ссылку на изображение
@dp.message(AddProductStates.waiting_for_image_link)
async def receive_image_link(message: types.Message, state: FSMContext):
    image_link = message.text.strip()
    await state.update_data(image_link=image_link)
    await message.answer("Введите цену товара:")
    await state.set_state(AddProductStates.waiting_for_price)


# Получаем цену товара
@dp.message(AddProductStates.waiting_for_price)
async def receive_price(message: types.Message, state: FSMContext):
    try:
        price = float("".join(message.text.split()).replace(',', '.'))
        await state.update_data(price=price)
        await message.answer("Введите марку машины:")
        await state.set_state(AddProductStates.waiting_for_type_car)
    except ValueError:
        await message.answer(
            "Некорректный формат цены. Используйте цифры и точку/запятую.")


# Получаем тип машины изображение
@dp.message(AddProductStates.waiting_for_type_car)
async def receive_image_link(message: types.Message, state: FSMContext):
    type_car = sercher(message.text.strip())
    if type_car is not None:
        await state.update_data(type_car=type_car)
        await message.answer("Введите название:")
        await state.set_state(AddProductStates.waiting_for_title)
    else:
        await message.answer("Такой марки я не знаю!")


# Получаем название товара
@dp.message(AddProductStates.waiting_for_title)
async def receive_title_and_save(message: types.Message, state: FSMContext):
    title = message.text.strip()
    user_data = await state.get_data()
    yandex_link = user_data['yandex_link']
    image_link = user_data['image_link']
    price = user_data['price']
    type_car = user_data['type_car']

    # Сохраняем данные в базу
    cursor.execute(
        'INSERT INTO all_cars (title, image_link, price, yandex_link, type_car) VALUES (?, ?, ?, ?, ?)',
        (title, image_link, price, yandex_link, type_car))
    conn.commit()
    await message.answer("Машина успешно добавлена!")
    await state.clear()


@dp.callback_query(lambda call: True)
async def handle_callback_query(call: types.CallbackQuery):
    await call.answer("Запрашиваю данные...", cache_time=5)


@dp.message(F.text)
async def process_user_query(message: types.Message):
    user_input = message.text
    result = search_car(user_input)

    if result:
        answer_text = (
            f"<b>{result['title']}</b>\n\n"
            f"Цена: {result['price']}\n\n"
            f"Ссылка: {result['link']}"
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=result['image_url'],
            caption=answer_text,
            parse_mode='HTML'
        )
    else:
        await message.answer("Такая марка машины не найдена.")


# Функция запуска бота
async def main_tovar():
    global bot
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)
