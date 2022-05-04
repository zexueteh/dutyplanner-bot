import os, csv
from datetime import datetime, time
from dotenv import load_dotenv
import pytz


import logging
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, InlineQueryHandler, CallbackQueryHandler

from utility import start_function, welcome_function, leave_function
from duty_reminders import reminder_function, reminder_response
from upload_file import upload_function
from manage_data import manage_duty, manage_DP, manage_update
from choose_duty_inline import choosing_function, choice_response


# Enable logging
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



def main():
    load_dotenv()
    updater = Updater(os.environ.get("my_token"))
    dispatcher = updater.dispatcher
    queue = updater.job_queue

    dispatcher.add_handler(MessageHandler(filters = Filters.status_update.new_chat_members, callback = welcome_function))

    dispatcher.add_handler(CommandHandler(command = "start", callback = start_function))
    
    # Admin Commands/Functionality
    admin_filter = Filters.user(int(os.environ.get("admin_id")))
    dispatcher.add_handler(MessageHandler(filters = Filters.document.file_extension("csv") & admin_filter, callback = upload_function))

    # Admin command to manage csv data/ DP usernames 
    dispatcher.add_handler(CommandHandler(filters = admin_filter, command = "manage", callback = manage_duty))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback = manage_DP, pattern = "MANAGE_DUTY"))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback = manage_update, pattern = "MANAGE_DP"))


    
    # Admin Group Command to choose duties and handler for choosing responses
    dispatcher.add_handler(CommandHandler(filters = admin_filter, command = "choose", callback = choosing_function))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback = choice_response, pattern = "SLOT")) 
    updater.dispatcher.add_handler(CallbackQueryHandler(callback = choosing_function, pattern = "REFRESH")) 
    
    # 2200 special reminder for 0730 duties
    queue.run_daily(callback = reminder_function, days = (0, 1, 2, 3, 4, 5, 6), time = time(hour = 22, minute = 0, second = 0, tzinfo = pytz.timezone("Asia/Singapore")))

    # 0830 reminder for duties
    queue.run_daily(callback = reminder_function, days = (0, 1, 2, 3, 4, 5, 6), time = time(hour = 8, minute = 30, second = 0, tzinfo = pytz.timezone("Asia/Singapore")))

    # Handler for reminder responses
    updater.dispatcher.add_handler(CallbackQueryHandler(callback = reminder_response, pattern = "REMIND"))


    updater.start_polling()
    

if __name__ == "__main__":
    main()