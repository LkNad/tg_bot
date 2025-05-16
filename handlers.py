from telegram import Update, InputFile
from telegram.ext import ConversationHandler
from telegram.ext import ContextTypes
import requests
import os
import csv
from datetime import datetime

GET_CITY, GET_STREET = range(2)

user_context = {}


def save_user_data(user_id, city, street):
    os.makedirs("data", exist_ok=True)
    with open("data/users.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), user_id, city, street])


def log_activity(user_id, message):
    with open("data/logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user_id}: {message}\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я помогу найти ближайшие магазины. Введите ваш город.")
    return GET_CITY


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Использование:\n/start — начать поиск\n/help — помощь\n/cancel — отменить"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Поиск отменён.")
    return ConversationHandler.END


async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_context[user_id] = {"city": update.message.text}
    await update.message.reply_text("Отлично! Теперь укажите улицу.")
    return GET_STREET


async def ask_street(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_context[user_id]["street"] = update.message.text
    city = user_context[user_id]["city"]
    street = user_context[user_id]["street"]

    log_activity(user_id, f"Запрос: {city}, {street}")
    save_user_data(user_id, city, street)

    await update.message.reply_text(f"Ищу магазины около {city}, {street}...")
    await find_shops(update, context, city, street)
    return ConversationHandler.END


async def find_shops(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str, street: str):
    address = f"{street}, {city}"
    location = get_coordinates(address)

    if not location:
        await update.message.reply_text("Не удалось найти координаты. Попробуйте снова.")
        return

    lat, lon = location
    shops = query_overpass(lat, lon)

    if not shops:
        await update.message.reply_text("Магазины не найдены.")
        return

    for shop in shops[:5]:
        name = shop.get("tags", {}).get("name", "Магазин без названия")
        distance = shop.get("distance", "Неизвестно")
        await update.message.reply_text(f"{name} — около {distance:.0f} м")

        if os.path.exists("images/shop.png"):
            with open("images/shop.png", "rb") as img:
                await update.message.reply_photo(photo=InputFile(img))


#Геокодирование через Nominatim
def get_coordinates(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    headers = {"User-Agent": "SimpleTelegramBot"}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])


#Поиск магазинов через Overpass API
def query_overpass(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    radius = 1000
    query = f"""
    [out:json];
    (
      node["shop"](around:{radius},{lat},{lon});
    );
    out body;
    """
    response = requests.post(overpass_url, data=query.encode("utf-8"))
    data = response.json()
    elements = data.get("elements", [])
    for elem in elements:
        elem["distance"] = haversine(lat, lon, elem["lat"], elem["lon"])
    elements.sort(key=lambda x: x["distance"])
    return elements


#Расчёт расстояния по формуле гаверсина
from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))
