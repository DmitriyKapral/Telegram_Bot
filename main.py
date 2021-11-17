import logging
import locale
import datetime
import pytz
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Привет! Используй /add <Название> -t <Число> в <Время> чтобы поставить напоминание\nПример: /add Купить хлеба -t завтра в 18:00\n/add Выключить чайник -t 21.11.21 16:00')
    update.message.reply_text('Так же ты можешь просмотреть свой список напоминаний! Используй /all')
    update.message.reply_text('Если какие то напоминания ты создал по ошибке, или они больше не нужны, то используй /del <id Напоминания> !')


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text="Напоминание на " + job.name)


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def all_list(update: Update, context: CallbackContext) -> bool:
    allList = context.job_queue.jobs()
    index = 1
    update.message.reply_text("Список:\n")
    for b in allList:
        update.message.reply_text("id " + str(index) + ": " + b.name)
        index+=1

def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    locale.setlocale(locale.LC_ALL, "ru")
    chat_id = update.message.chat_id
    try:
        strs = ""
        for i in range(len(context.args)):
            #if context.args[i] == "-t":
                #break
            strs += context.args[i] + " "
            if context.args[i] == "-t":
                index = i
        
        date = context.args[index+1]
        if date == "завтра" or date == "Завтра":
            tomorrow_date = datetime.datetime.today()
            tomorrow_date += datetime.timedelta(days=1)
            if context.args[index+2] != "в":
                return
            t = re.split(r':', context.args[index+3])
            desired_date = tomorrow_date.replace(hour=int(t[0]), minute=int(t[1]))
            timezone_newyork = pytz.timezone('Europe/Moscow')
            desired_date = timezone_newyork.localize(desired_date)
        elif date == "послезавтра" or date == "Послезавтра":
            day_after_tomorrow_date = datetime.datetime.today()
            day_after_tomorrow_date += datetime.timedelta(days=2)
            if context.args[index+2] != "в":
                return
            t = re.split(r':', context.args[index+3])
            desired_date = day_after_tomorrow_date.replace(hour=int(t[0]), minute=int(t[1]))
            timezone_newyork = pytz.timezone('Europe/Moscow')
            desired_date = timezone_newyork.localize(desired_date)
        else:
            desired_date = datetime.datetime.strptime(date + " " + context.args[index+2], '%d.%m.%Y %H:%M')
            timezone_newyork = pytz.timezone('Europe/Moscow')
            desired_date = timezone_newyork.localize(desired_date)
        
        strs = strs[:-1]
        name_date = desired_date.strftime("%d.%m.%Y в %H:%M")
        result = re.split(r' -t ', strs)
        context.job_queue.run_once(alarm, desired_date, context=chat_id, name=name_date + " - '" + result[0] + "'")
        #ВЫВОД ТЕКСТА
        a = context.job_queue.jobs()
        text = 'Напоминание создано!'
        update.message.reply_text(text)
        

    except (IndexError, ValueError):
        update.message.reply_text('Используй: /add <Название> -t <Число> в <Время>')

def delete_job(update: Update, context: CallbackContext) -> None:
    i = int(context.args[0])
    allList = context.job_queue.jobs()
    index = 0
    for b in allList:
        index += 1
        if index == i:
            remove_job_if_exists(b.name, context)
            update.message.reply_text("Напоминание на " + b.name + " удалено!")
        else:
            return


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("add", set_timer))
    dispatcher.add_handler(CommandHandler("del", delete_job))
    dispatcher.add_handler(CommandHandler("all", all_list))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


