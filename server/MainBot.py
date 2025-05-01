import asyncio
from ctypes import pythonapi

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from tovar_bot import *
from config import BOT_TOKEN_shifred
import config_botT
import logging
import sys
import subprocess
import os

# Защита от посторонних глаз
from de_shifre import de_shifre
BOT_TOKEN = de_shifre(BOT_TOKEN_shifred)


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
    button2 = types.InlineKeyboardButton(text="Товар", callback_data="tovar", url="http://t.me/Dostoprimechatelnost_HeBot")
    button3 = types.InlineKeyboardButton(text="Еда",
                                         url="http://t.me/Eda_HeBot")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [button1],
        [button2],
        [button3]
    ])

    await message.reply("Привет! Выбери, что ты хочешь найти:",
                        reply_markup=keyboard)


# Обработчик нажатия кнопки Товара
@dp.callback_query(lambda call: call.data == 'tovar')
async def handle_tovar_button(call: types.CallbackQuery):
    global open_tovar
    # Подтверждение выбора
    await call.answer("Запускаю поиск товаров...")

    # Закрываем соединение с ботом и прекращаем обработку событий
    open_tovar = True
    await bot.session.close()
    await dp.stop_polling()

    # Запускаем новую программу



if __name__ == '__main__':
    asyncio.run(main())
    if open_tovar:
        asyncio.run(main_tovar())
