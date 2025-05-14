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

    await update.message.reply_text(f"Город {city_ru} принят. Ищу достопримечательности...")

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

    # Ищем описания достопримечательностей
    description_divs = soup.find_all("div", class_="img_right2")
    descriptions = [div.get_text(strip=True) for div in description_divs[:2]]

    # Ищем изображения
    img_tags = soup.find_all('img')

    if len(img_tags) <= 7:
        await update.message.reply_text("Недостаточно изображений для фильтрации.")
        return

    filtered_tags = img_tags[6:-1]
    image_links = []

    for tag in filtered_tags:
        width = tag.get('width')
        height = tag.get('height')

        try:
            w = int(width)
            h = int(height)
        except (TypeError, ValueError):
            continue

        if w >= 100 and h >= 100:
            matches = re.findall(r'https://[^\s]+\.jpg', str(tag))
            if matches:
                image_links.append(matches[0])
            if len(image_links) == 2:
                break

    # Отправляем по очереди: картинка и описание
    if not image_links:
        await update.message.reply_text("Не удалось найти подходящие изображения.")
    else:
        for i in range(len(image_links)):
            await update.message.reply_photo(photo=image_links[i])
            if i < len(descriptions):
                await update.message.reply_text(descriptions[i])



def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))

    print("Бот запущен. Напишите ему /start.")
    app.run_polling()

if __name__ == "__main__":
    main()