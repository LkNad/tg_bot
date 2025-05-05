import asyncio
from ctypes import pythonapi

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pyexpat.errors import messages

from tovar_bot import *
from config import BOT_TOKEN
import logging
import sys
import subprocess
import os

# Защита от посторонних глаз



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

dp = Dispatcher()
bot = None

open_tovar = False


async def main():
    global bot
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def process_start_command(message: types.Message):
    button1 = types.InlineKeyboardButton(text="Достопримечательность",
                                         url="http://t.me/Dostoprimechatelnost_HeBot")
    button2 = types.InlineKeyboardButton(text="Товар", callback_data="tovar")
    button3 = types.InlineKeyboardButton(text="Еда",
                                         url="http://t.me/Eda_HeBot")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [button1],
        [button2],
        [button3]
    ])

    await message.reply("Привет! Выбери, что ты хочешь найти:",
                        reply_markup=keyboard)


@dp.callback_query(lambda call: call.data == 'tovar')
async def handle_tovar_button(call: types.CallbackQuery):
    global open_tovar
    # Подтверждение выбора
    await call.answer("Запускаю поиск товаров...")


if __name__ == '__main__':
    asyncio.run(main())
