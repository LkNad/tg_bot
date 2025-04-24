import sqlite3
import asyncio
from idlelib.run import Executive

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
from config import BOT_TOKEN
from config_botT import DEVS_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USERS_NAMES_ID = set()
old_main = None


class AddProductStates(StatesGroup):
    waiting_for_yandex_link = State()
    waiting_for_image_link = State()
    waiting_for_price = State()
    waiting_for_title = State()


conn = sqlite3.connect('yandex_market.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    image_link TEXT,
    price REAL,
    yandex_link TEXT
);
''')
conn.commit()


# Обработчик старта (/start и /help), выводящий приветствие и доступный список команд
@dp.message(Command('start'))
@dp.message(Command('help'))
async def start_command(message: types.Message):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    help_message = """
        Привет! Это бот для добавления товаров в каталог.
        Доступные команды:
        /develop - показывает список всех комманд (только для разработчиков)
        /help or /start - выводит список комманд
        """
    await message.answer(help_message)




@dp.message(Command('develop'))
async def start_command(message: types.Message):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    if message.from_user.id in DEVS_ID:
        help_message = """
        /add_tovar - добавить новый товар (только для разработчиов)
        /help or /start - выводит список комманд
        /develop - показывает список всех комманд (только для разработчиков)
        /add_dev - добавление нового временного разработчика
        /all_id - выводит список всех id и никноймов пользователей
        """
        await message.answer(help_message)
    else:
        await message.answer(
            "У вас недостаточно прав для выполнения данной команды.")


# Обработчик команды /add_tovar
@dp.message(Command('add_tovar'))
async def add_new_product(message: types.Message, state: FSMContext):
    global USERS_NAMES_ID
    USERS_NAMES_ID.add(
        f'{message.from_user.id} '
        f' - {message.from_user.full_name}'
        f'(@{message.from_user.username})')

    if message.from_user.id in DEVS_ID:
        await message.answer("Отправьте ссылку на товар:")
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
        price = float(message.text.replace(',', '.'))
        await state.update_data(price=price)
        await message.answer("Введите название товара:")
        await state.set_state(AddProductStates.waiting_for_title)
    except ValueError:
        await message.answer(
            "Некорректный формат цены. Используйте цифры и точку/запятую.")


# Получаем название товара
@dp.message(AddProductStates.waiting_for_title)
async def receive_title_and_save(message: types.Message, state: FSMContext):
    title = message.text.strip()
    user_data = await state.get_data()
    yandex_link = user_data['yandex_link']
    image_link = user_data['image_link']
    price = user_data['price']

    # Сохраняем данные в базу
    cursor.execute(
        'INSERT INTO products (title, image_link, price, yandex_link) VALUES (?, ?, ?, ?)',
        (title, image_link, price, yandex_link))
    conn.commit()
    await message.answer("Товар успешно добавлен!")
    await state.clear()


@dp.callback_query(lambda call: True)
async def handle_callback_query(call: types.CallbackQuery):
    await call.answer("Запрашиваю данные...", cache_time=5)


@dp.message(F.text)
async def search_product(message: types.Message):
    user_input = message.text.lower()
    cursor.execute(
        "SELECT title, image_link, price, yandex_link FROM products WHERE LOWER(title) LIKE ?",
        ('%' + user_input + '%',))
    result = cursor.fetchone()
    if result:
        title, image_link, price, yandex_link = result
        answer_text = f"""
            Название: {title}
            Цена: {price:.2f} руб.
            Ссылка на фото: {image_link}
            Ссылка на товар: {yandex_link}
            """
        await message.answer(answer_text)
    else:
        await search_product(message)
        # await message.answer("Не удалось найти товар.")


@dp.message(F.text)
async def search_product(message: types.Message):
    user_input = "+".join(message.text.lower().split())
    await message.answer(f'''Вот что я смог найти на алиэкспрес:\n
    https://aliexpress.ru/wholesale?SearchText={user_input}
        ''')


# Функция запуска бота
async def main_tovar(old = None):
    global old_main
    old_main = old
    await dp.start_polling(bot)


# Запускаем бота
if __name__ == "__main__":
    main_tovar()
