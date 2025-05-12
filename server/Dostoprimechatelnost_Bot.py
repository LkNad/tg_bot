from deep_translator import GoogleTranslator
from config import BOT_TOKEN
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import re

# Регулярное выражение для поиска ссылок
pattern = r'https://[^\s]+\.jpg'

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напишите город, в котором вы хотите найти достопримечательности.")

# Обработка ввода города и отправка изображений
async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_ru = update.message.text
    context.user_data["city_ru"] = city_ru

    await update.message.reply_text(f"Город {city_ru} принят. Ищу фотографии...")

    # Перевод с русского на английский
    try:
        city_en = GoogleTranslator(source='ru', target='en').translate(city_ru)
    except Exception as e:
        await update.message.reply_text("Ошибка перевода названия города.")
        return

    # Заменяем пробелы на нижнее подчеркивание
    city_en = city_en.replace(" ", "_").lower()
    city_en = city_en.replace("ny_", "niy_")

    url = f"https://www.tourister.ru/world/europe/russia/city/{city_en}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        await update.message.reply_text(f"Не удалось получить данные с сайта по ссылке: {url}")
        return

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    if len(img_tags) <= 7:
        await update.message.reply_text("Недостаточно изображений для фильтрации.")
        return

    filtered_tags = img_tags[6:-1]
    result = []

    for tag in filtered_tags:
        width = tag.get('width')
        height = tag.get('height')

        try:
            w = int(width)
            h = int(height)
        except (TypeError, ValueError):
            continue

        if w >= 100 and h >= 100:
            result.append(tag)
            if len(result) == 2:
                break

    if not result:
        await update.message.reply_text("Не найдено подходящих изображений.")
    else:
        for tag in result:
            # Поиск всех совпадений
            matches = re.findall(pattern, str(tag))
            # Получение первой ссылки, если она существует
            first_link = matches[0] if matches else None
            await update.message.reply_text(first_link)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))

    print("Бот запущен. Напишите ему /start.")
    app.run_polling()

if __name__ == "__main__":
    main()