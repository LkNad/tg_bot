import asyncio
from ctypes import pythonapi

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pyexpat.errors import messages


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

OPEN_TOVAR = False


async def main():
    global bot
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def process_start_command(message: types.Message):
    button1 = types.InlineKeyboardButton(text="Достопримечательность",
                                         url="http://t.me/Dostoprimechatelnost_HeBot")
    button2_1 = types.InlineKeyboardButton(text="Поисковик авто (ссылка)",
                                         url="t.me/Tovar_HeBot")
    button2 = types.InlineKeyboardButton(text="запуск авто-поискового бота", callback_data="tovar")
    button3 = types.InlineKeyboardButton(text="Еда",
                                         url="http://t.me/Eda_HeBot")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [button1],
        [button2_1],
        [button2],
        [button3]
    ])

    await message.reply("""Привет! Выбери, что ты хочешь найти:""",
                        reply_markup=keyboard)



@dp.callback_query(lambda call: call.data == 'tovar')
async def handle_tovar_button(call: types.CallbackQuery):
    global bot
    await call.answer("Запускаю поиск товаров...", show_alert=True)
    await asyncio.create_task(start_tovar_mode())




async def start_tovar_mode():
    from tovar_bot import main_tovar
    await main_tovar()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Прервано вручную.")
