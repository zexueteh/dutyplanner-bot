import csv, requests, os, json
from dotenv import load_dotenv
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from read_data import _get_duty_message
from upload_file import _write_file

def manage_duty(update, context):
    # This command allows admin to insert/delete DP in monthly forecast
    # /manage mm yyyy, default values for mm and yyyy are current month and year

    # 1. validate command arguements
    # try:
    if context.args: # validating mm, yyyy and file existence
        mm, yyyy = int(context.args[0]), int(context.args[1])
        datetime(year = yyyy, month = mm, day = 1)
        open(f"forecasts/{mm}_{yyyy}.csv")
    else: # if no arguements assume current month
        now = datetime.now()
        mm, yyyy = now.month, now.year

    # 2. Create buttons to select which Duty
    with open("DP_usernames.json") as file:
        DP_dict = json.load(file) 
    dutys = []

    with open(f"forecasts/{mm}_{yyyy}.csv", encoding = "utf-8-sig") as file:
        for index, row in enumerate(csv.reader(file)):
            if len(row) == 5:
                row[4] = DP_dict[row[4]][0]
            dutys.append([InlineKeyboardButton(text = "  ".join(row), callback_data = f"MANAGE_DUTY|{mm}|{yyyy}|{index}")])
    
    # 3. Send forecast message plus buttons
    markup = InlineKeyboardMarkup(dutys)
    msg = _get_duty_message(mm, yyyy, "Choose a Duty slot")
    context.bot.send_message(chat_id = update.effective_chat.id, text = msg, reply_markup = markup, parse_mode = "HTML")
    # except Exception as err:
    #     print(err)
    #     context.bot.send_message(chat_id = update.effective_chat.id, text = "<pre>Invalid input. Try /manage mm yyyy, default mm, yyyy is current month and year</pre>", parse_mode = "HTML")
    

def manage_DP(update, context):
    # 1. Get data about which duty slot of which mm.yyyy to edit from callback_query
    query = update.callback_query.data.split("|") # query = "MANAGE_DP|mm|yyyy|index"
    mm, yyyy, duty_index = int(query[1]), int(query[2]), query[3]

    # 2. Generate inline keyboard of available DPs to insert at that slot
    DPs = [[InlineKeyboardButton(text = "N/A (delete)", callback_data = f"MANAGE_DP|{mm}|{yyyy}|{duty_index}|")]]
    with open("DP_usernames.json") as file:
        DP_dict = json.load(file)
        for id in DP_dict.keys():
            DPs.append([InlineKeyboardButton(text = f"{DP_dict[id][0]}", callback_data = f"MANAGE_DP|{mm}|{yyyy}|{duty_index}|{id}")])
    
    # 3. Update message and keyboard to prompt a choice
    new_markup = InlineKeyboardMarkup(DPs)
    new_msg = _get_duty_message(mm, yyyy, "Choose a Duty Personnel")
    update.effective_message.edit_text(text = new_msg, reply_markup = new_markup, parse_mode = "HTML")

def manage_update(update, context):

    # 1. Get data about DP to insert at duty slot at mm.yyyy from callback_query
    query = update.callback_query.data.split("|") # query = "MANAGE_DP|mm|yyyy|index|id"
    mm, yyyy, duty_index, DP_id = int(query[1]), int(query[2]), int(query[3]), query[4]
    with open("DP_usernames.json") as file:
        DP_dict = json.load(file)

    # 2. Open forecast file and update data, write back to forecast file
    with open(f"forecasts/{mm}_{yyyy}.csv", encoding = "utf-8-sig") as file:
        new_data = list(csv.reader(file))
        new_data[duty_index] = new_data[duty_index][:4]
        if DP_id:
            new_data[duty_index].append(DP_id)
    _write_file(f"forecasts/{mm}_{yyyy}.csv", new_data)

    # 3. Generate different messages for assigning a slot/clearing a slot
    if DP_id:
        footer = f"DP {DP_dict[DP_id][0]} assigned to {new_data[duty_index][2]}HRS {new_data[duty_index][3]} duty on {new_data[duty_index][0]}"
    else:
        footer = f"Cleared {new_data[duty_index][2]}HRS {new_data[duty_index][3]} duty on {new_data[duty_index][0]}"
        
    new_msg = _get_duty_message(mm, yyyy, footer)
    update.effective_message.edit_text(text = new_msg, parse_mode = "HTML")