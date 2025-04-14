# Импортируем необходимые классы.
import logging

from telegram.ext import Application, MessageHandler, filters, CommandHandler, \
    CallbackContext

from config import BOT_TOKEN, DEVS_ID

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import aiohttp

reply_keyboard = [['/start', '/help'], ['/set', '/unset']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

TIMER = 25
USERS = set()
USERS_NAMES_ID = set()
MAIN_DEVS = DEVS_ID.copy()

logger = logging.getLogger(__name__)


def get_ll_spn(toponym):
    ll = list(map(lambda x: str(x), toponym["Point"]["pos"].split()))
    lowercorner = list(map(lambda x: float(x), toponym["boundedBy"]["Envelope"][
        "lowerCorner"].split()))
    uppercorner = list(map(lambda x: float(x), toponym["boundedBy"]["Envelope"][
        "upperCorner"].split()))
    spn = list(map(lambda x: str(x), [uppercorner[0] - lowercorner[0],
                                      uppercorner[1] - lowercorner[1]]))
    return f'{ll[0]},{ll[1]}', f'{spn[0]},{spn[1]}'


async def geocoder(update, context):
    global USERS, USERS_NAMES_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')

    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = await get_response(geocoder_uri, params={
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "format": "json",
        "geocode": update.message.text
    })

    try:
        toponym = response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        ll, spn = get_ll_spn(toponym)
        # Можно воспользоваться готовой функцией,
        # которую предлагалось сделать на уроках, посвящённых HTTP-геокодеру.

        static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
        await context.bot.send_photo(
            update.message.chat_id,
            # Идентификатор чата. Куда посылать картинку.
            # Ссылка на static API, по сути, ссылка на картинку.
            # Телеграму можно передать прямо её, не скачивая предварительно карту.
            static_api_request,
            caption="Нашёл твой адрес на яндекс карте!"
        )
    except Exception:
        chat_id = update.effective_message.chat_id
        await context.bot.send_message(chat_id=chat_id,
                                       text='Не удалось найти твой адрес :(')


async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def task(context):
    global TIMER
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id,
                                   text=f'ЙОУ! Твой таймер в размере: {TIMER}c. закончился!')
    TIMER = 25


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# Обычный обработчик, как и те, которыми мы пользовались раньше.
async def set_timer(update, context):
    global USERS, USERS_NAMES_ID, TIMER
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')

    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    try:
        TIMER = int(context.args[0])
        if TIMER < 0:
            TIMER = 0
    except Exception:
        pass
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id,
                               name=str(chat_id),
                               data=TIMER)

    text = f'Вернусь через {TIMER} с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def unset(update, context):
    global USERS, USERS_NAMES_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')

    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
async def start(update, context):
    global USERS, USERS_NAMES_ID
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот, который поможет найти любое место на карте по его адресу!",
        reply_markup=markup
    )
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')


async def close_keyboard(update, context):
    global USERS
    USERS.add(update.effective_chat.id)
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


async def global_message(update, context):
    global USERS, USERS_NAMES_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')

    """Функция для отправки сообщения всем пользователям"""
    if not update.message.text.startswith('/global '):
        return

    message_to_send = update.message.text.replace('/global ', '')
    for user in USERS:
        try:
            await context.bot.send_message(chat_id=user, text=message_to_send)
        except Exception as e:
            print(f'Не удалось отправить сообщение пользователю {user}: {e}')


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    if len(context.args) == 0:
        await update.message.reply_text(
            f'''Как работают комманды?\n
            /set {'{число} (по умолчанию:25)'} - устанавливает таймер на заданное кол-во секунд\n
            /unset - удаляет таймер\n
            /start - начинает программу и показывает список комманд\n
            /help {'{ + } (по умолчанию: "" )'} - помощь\n
            \n
            Напиши адрес боту и он найдёт его на карте!\n
            ''')
    elif len(context.args) == 1 and context.args[
        0] == '+' and update.effective_chat.id in DEVS_ID:
        await update.message.reply_text(f'''Как работают комманды для разработчиков?\n
                   /spam {'{user id} {text} {count}'} - отправляет сообщения заданному пользователю\n
                   /all_id - показывает список id\n
                   /clear_id - очищает список id\n
                   /global {'{text}'} - отправляет глобальное сообщение всем пользователям\n
                   /help + - показывает список секретных команд\n
                   /add_dev {'{dev_id}'} - добавляет нового администратора\n
                   /clear_devs - удаляет всех администраторов кроме главных\n
                   ''')
    else:
        await update.message.reply_text(
            """Неверное написание комадны /help\n""")


async def spam(update, context):
    global USERS, USERS_NAMES_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')

    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    if chat_id in DEVS_ID:
        try:
            user = context.args[0]
            text = " ".join(list(context.args[1:-1]))
        except Exception:
            try:
                text = " ".join(list(context.args[0:-1]))
                user = chat_id
            except Exception:
                user = chat_id
                text = ''

        try:
            for i in range(int(context.args[-1])):
                await context.bot.send_message(chat_id=user, text=text)
        except Exception:
            await context.bot.send_message(chat_id=chat_id,
                                           text='Не верный USER_ID, текст или кол-во сообщений!')
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='У вас нет доступа к этой команде!')


async def get_users(update, context):
    global USERS, USERS_NAMES_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')

    chat_id = update.effective_message.chat_id
    if chat_id in DEVS_ID:
        messages = f"{'\n'.join(list(map(str, USERS_NAMES_ID)))}"
        await context.bot.send_message(chat_id=chat_id, text=messages)
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='У вас нет доступа к этой команде!')


async def clear_id(update, context):
    global USERS, USERS_NAMES_ID
    chat_id = update.effective_message.chat_id
    if chat_id in DEVS_ID:
        USERS = set()
        USERS_NAMES_ID = set()
        USERS.add(update.effective_chat.id)
        USERS_NAMES_ID.add(
            f'{update.effective_chat.id} '
            f' - {update.effective_chat.full_name}'
            f'(@{update.effective_chat.username})')

        messages = "Все айди успешно удалены!"
        await context.bot.send_message(chat_id=chat_id, text=messages)
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='У вас нет доступа к этой команде!')


async def add_developer(update, context):
    global USERS, USERS_NAMES_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')
    print(f'{DEVS_ID} - old')

    chat_id = update.effective_message.chat_id
    if chat_id in DEVS_ID:
        try:
            DEVS_ID.add(int(context.args[0]))
            await context.bot.send_message(chat_id=chat_id,
                                           text='Успешно!')
        except Exception:
            await context.bot.send_message(chat_id=chat_id,
                                           text='Не верный USER_ID')
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='У вас нет доступа к этой команде!')
    print(f'{DEVS_ID} - new')


async def clear_devs(update, context):
    global USERS, USERS_NAMES_ID, DEVS_ID
    USERS.add(update.effective_chat.id)
    USERS_NAMES_ID.add(
        f'{update.effective_chat.id} '
        f' - {update.effective_chat.full_name}'
        f'(@{update.effective_chat.username})')
    print(f'{DEVS_ID} - old')

    chat_id = update.effective_message.chat_id
    if chat_id in DEVS_ID:
        DEVS_ID = MAIN_DEVS
        await context.bot.send_message(chat_id=chat_id,
                                       text='Успешно!')
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text='У вас нет доступа к этой команде!')
    print(f'{DEVS_ID} - new')


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
async def echo(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    await update.message.reply_text(update.message.text)


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    # text_handler = MessageHandler(filters.TEXT, echo)
    my_text_handler = MessageHandler(filters.TEXT, geocoder)

    # Зарегистрируем их в приложении перед
    # регистрацией обработчика текстовых сообщений.
    # Первым параметром конструктора CommandHandler я
    # вляется название команды.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("close", close_keyboard))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("global", global_message))
    application.add_handler(CommandHandler("spam", spam))
    application.add_handler(CommandHandler("all_id", get_users))
    application.add_handler(CommandHandler('clear_id', clear_id))
    application.add_handler(CommandHandler('add_dev', add_developer))
    application.add_handler(CommandHandler('clear_devs', clear_devs))
    # /global - комманда для отправки глобального сообщения всем пользователям

    # Регистрируем обработчик в приложении.
    # application.add_handler(text_handler)
    application.add_handler(my_text_handler)
    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
