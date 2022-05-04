import csv, os
from datetime import date, timedelta
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from read_data import _get_duty_message
from upload_file import _write_file, _add_user


load_dotenv()
admin_id = int(os.environ.get("admin_id"))
month_dict = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}

def _get_slots(mm, yyyy):
    slots = [[InlineKeyboardButton(text = "REFRESH SLOTS", callback_data = f"REFRESH|{mm}|{yyyy}")]]

    with open(f"forecasts/{mm}_{yyyy}.csv", encoding = "utf-8-sig") as file:
        for index, row in enumerate(csv.reader(file)):
            if len(row) == 4:
                slots.append([InlineKeyboardButton(text = f"{row[0]}  {row[2]}  {row[3]}", callback_data = f"SLOT{index}")])

    return InlineKeyboardMarkup(slots)



def choosing_function(update, context):
    # 1. Determine if function is sending new message (/choose command), or updating an existing message for specific mm yyyy (REFRESH button)
    if update.callback_query == None:
        choosing_datetime = date.today() + timedelta(days = 28)
        mm, yyyy = choosing_datetime.month, choosing_datetime.year

    elif "REFRESH" in update.callback_query.data:
        #mm, yyyy = 5, 2022
        mm, yyyy = int(update.callback_query.data.split("|")[1]), int(update.callback_query.data.split("|")[2])

    # 2. get duty message and inline keyboard based on mm, yyyy
    slots = _get_slots(mm, yyyy)
    msg = _get_duty_message(mm, yyyy)

    # 3. Either send a new message, or update existing message
    if update.callback_query == None:
        context.bot.send_message(chat_id = update.effective_chat.id, text = msg, reply_markup = slots, parse_mode = "HTML")
    
    elif "REFRESH" in update.callback_query.data:
        try:
            update.effective_message.edit_text(text = msg, reply_markup = slots, parse_mode = "HTML")
        except:
            return #to mitigate telegram.error.BadRequest: Message is not modified
    



def choice_response(update, context):
    
    # 1. get the id, name of the DP that made the particular update, update the DP_username.json file
    _add_user(update.effective_user)
    DP_name = update.effective_user.first_name
    query = update.callback_query

    # 2. Read the forecast file to determine which slot was chosen, write back into forecast file
    chosen_index = int(query.data[4:])
    choosing_datetime = date.today() + timedelta(days = 28) # Can only choose duties for subsequent month
    choosing_filename = f"forecasts/{choosing_datetime.month}_{choosing_datetime.year}.csv"

    with open(choosing_filename, encoding = "utf-8-sig") as file:
        new_data = list(csv.reader(file))
        if len(new_data[chosen_index]) > 4: # Optimize code by ending function when row already picked
            return
        new_data[chosen_index].append(update.effective_user.id)
    _write_file(choosing_filename, new_data)

    # 3. Update the global slots by removing chosen duty
    new_slots =  _get_slots(choosing_datetime.month, choosing_datetime.year)
    new_message = _get_duty_message(choosing_datetime.month, choosing_datetime.year, f"{DP_name} has picked duty on {new_data[chosen_index][0]}")
    update.effective_message.edit_text(text = new_message, reply_markup = new_slots, parse_mode = "HTML")
        