import csv
import os
import logging
from aiohttp import ClientSession
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
ASK_LOCATION = 1
CSV_PATH = "data/results.csv"
ICON_PATH = "data/icons/store.png"

# Убедимся, что папка и файл есть
os.makedirs("data/icons", exist_ok=True)
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, mode='w', newline= '') as file:
        writer = csv.writer(file)
        writer.writerow(["user_id", "store_name", "lat", "lon"])


# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        "Я помогу тебе найти магазины с едой поблизости.\n"
        "Используй команду /find чтобы начать поиск."
    )


# Помощь
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — начать работу с ботом\n"
        "/help — показать справку\n"
        "/find — найти магазины с едой рядом"
    )


# Запрос локации
async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("Отправить локацию", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Пожалуйста, отправь свою локацию:", reply_markup=reply_markup)
    return ASK_LOCATION


# Обработка локации
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.location:
        await update.message.reply_text("Пожалуйста, отправь свою локацию.")
        return ASK_LOCATION

    lat = update.message.location.latitude
    lon = update.message.location.longitude
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} отправил локацию: {lat}, {lon}")

    stores = await search_food_shops(lat, lon)
    if not stores:
        await update.message.reply_text("Магазины не найдены.")
        return ConversationHandler.END

    for store in stores:
        name = store.get("name", "Без названия")
        store_lat = store["lat"]
        store_lon = store["lon"]

        # Сохраняем в CSV
        with open(CSV_PATH, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, name, store_lat, store_lon])

        # Отправка картинки и информации
        text = f"Название: {name}\nКоординаты: {store_lat}, {store_lon}"
        if os.path.exists(ICON_PATH):
            await update.message.reply_photo(photo=InputFile(ICON_PATH), caption=text)
        else:
            await update.message.reply_text(text)

    return ConversationHandler.END


# Запрос в OpenStreetMap API
async def search_food_shops(lat: float, lon: float):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["shop"="supermarket"](around:1000,{lat},{lon});
      node["shop"="convenience"](around:1000,{lat},{lon});
    );
    out body;
    """
    async with ClientSession() as session:
        async with session.post(overpass_url, data={"data": query}) as resp:
            if resp.status != 200:
                return []

            data = await resp.json()
            elements = data.get("elements", [])
            shops = []

            for el in elements:
                if "lat" in el and "lon" in el:
                    shops.append({
                        "name": el.get("tags", {}).get("name", "Без названия"),
                        "lat": el["lat"],
                        "lon": el["lon"]
                    })

            return shops[:5]  # Максимум 5 магазинов


# Обработка неизвестных сообщений
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда. Напиши /help для списка команд.")


# Главное
def main():
    app = ApplicationBuilder().token("8037121639:AAFmcV4cmvhbdP8if8N68lGXXF6XWFJ6IwY").build()

    # Хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("find", find_command)],
        states={ASK_LOCATION: [MessageHandler(filters.LOCATION, location_handler)]},
        fallbacks=[],
    )
    app.add_handler(conv_handler)

    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
