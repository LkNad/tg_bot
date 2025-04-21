import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


dp = Dispatcher()


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def process_start_command(message: types.Message):

    button1 = types.InlineKeyboardButton(text="Достопримечательность", url="http://t.me/Dostoprimechatelnost_HeBot")
    button2 = types.InlineKeyboardButton(text="Товар", url="http://t.me/Tovar_HeBot")
    button3 = types.InlineKeyboardButton(text="Еда", url="http://t.me/Eda_HeBot")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [button1],
        [button2],
        [button3]
    ])

    await message.reply("Привет! Выбери, что ты хочешь найти:", reply_markup=keyboard)


if __name__ == '__main__':
    asyncio.run(main())
