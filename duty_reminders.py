import csv, os, json, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import time
from prettytable import PrettyTable

from upload_file import _add_user

# opening DP username dictionary and creating global variables
load_dotenv() 
duty_chat_id, admin_username, admin_id = int(os.environ.get("duty_chat_id")), str(os.environ.get("admin_username")), int(os.environ.get("admin_id"))


def _generate_reminder_msg(num, name, type, HHMM, response):
    # 1. Initialize 2 tables each without headers for the reminder message itself and response
    msg_table, response_table = PrettyTable(), PrettyTable()
    msg_table.header, response_table.header = False, False
    
    # 2. format reminder message using arguements
    rows = [[f"REMINDER DP{num} {name} HAS"],
    [f"{type} DUTY @ {HHMM}HRS"],
    [f"PLEASE ACKNOWLEDGE"]]
    msg_table.add_rows(rows)
    
    # 3. format response message using left/right spaces as padding, same table size as reminder table
    no_padding = (len(rows[0][0]) - len(response))//2
    response = " "*no_padding + str(response) + " "*no_padding
    if len(response) < len(rows[0][0]):
        response += " "
    response_table.add_row([response])

    if HHMM == "0730": # 4. Handles extra message header based on duty shift, 0730 shift reminders sent the previous day.
        return "REMINDER TMRW 0730 DUTY\n" + "\n".join(str(msg_table).split("\n")[:4]) + "\n" + str(response_table)
    else:
        return "\n".join(str(msg_table).split("\n")[:4]) + "\n" + str(response_table)




# Daily reminder at 0830 for all personnel on duty on that particular day
def reminder_function(context):
    # 1. Get current forecast file to parse 
    now = datetime.now()
    file_name = f"forecasts/{now.month}_{now.year}.csv"

    # 2. Decide criteria to select reminders based on function call time
    if now.hour == 8:
        func = lambda row: (str(now.day) == row[0] and row[2] != "0730")
    elif now.hour == 22:
        func = lambda row: (str(now.day + 1) == row[0] and row[2] == "0730")


    with open("DP_usernames.json") as file:
        DP_dict = json.load(file)
    with open(file_name, encoding = "utf-8-sig") as file:
        for index, row in enumerate(csv.reader(file)):
            # 3. Find Duty ased on criteria and send reminder message 
            if func(row):
                    msg = _generate_reminder_msg(row[1], DP_dict[row[4]][0], row[3], row[2], "") # num, name, type, shift, response = ""
                    markup = InlineKeyboardMarkup([[InlineKeyboardButton("ACKNOWLEDGED", callback_data = f"REMIND|ACKN|{index}")], 
                    [InlineKeyboardButton("REMIND ME", callback_data = f"REMIND|CALL|{index}")], 
                    [InlineKeyboardButton("IM UNAVAILABLE", callback_data = f"REMIND|ALRT|{index}")]])
                    context.bot.send_message(text = "<pre>" + msg + "</pre>", reply_markup = markup, chat_id = duty_chat_id, parse_mode = "HTML")


def reminder_response(update, context):
    # 1. Get current forecast file to parse 
    now = datetime.now()
    file_name = f"forecasts/{now.month}_{now.year}.csv"
    with open("DP_usernames.json") as file:
        DP_dict = json.load(file)

    # 1. get response query and format callback data accordingly
    query = update.callback_query.data.split("|")
    response, index = query[1], int(query[2])# data format -> Pattern|ResponseCode|index

    with open(file_name) as file:
        file_data = list(csv.reader(file))
    row = file_data[index]
    Num, Name, Type, HHMM = row[0], DP_dict[row[4]][0], row[1], row[2]

    DP = _add_user(update.effective_user)

    if str(update.effective_user.id) == id:
        # Case 1: DP acknowledges, update ACKNOWLEDGED as response
        if response == "ACKN":
            new_message = _generate_reminder_msg(Num, Name, Type, HHMM, "ACKNOWLEDGED")

        # Case 2: DP requests a reminder
        elif response == "CALL":
            # 2.1 Calculate time until 15 minutes before duty
            now = datetime.now()
            shift_time = datetime(year = now.year, month = now.month, day = now.day, hour = int(HHMM[:2]), minute = int(HHMM[2:]))
            sleep_time = (shift_time - now).seconds - 15*60

            # 2.2 Generate update with REMIND as response
            remind_time = (shift_time - timedelta(minutes = 15.0)).strftime("%H%M")
            new_message = _generate_reminder_msg(Num, Name, Type, HHMM, f"REMIND @ {remind_time}HRS")

            update.effective_message.edit_text(text = "<pre>" + new_message + "</pre>", parse_mode = "HTML")

            # 2.3 Sleep until 15 mins before duty, use callmebot to call DP.
            #sleep_time = 15
            time.sleep(sleep_time)

            if not DP[id][1].isdigit():
                username = "@" + DP[id][1]
            voice_message = "%20".join(["HELLO", "HELLO", DP[id][0], "REMINDER", "REMINDER", "YOU", "HAVE", "DUTY", "AT", HHMM, "HOURS"])
            web_api = f"http://api.callmebot.com/start.php?source=auth&user={username}&text={voice_message}&lang=en-IN-Standard-B"
            r = requests.get(web_api)

            # 2.5 Error case, call fails due to following reasons.
            callmebot_errors = ["FLOOD", "SPAM", "User not authorized"]
            for err in callmebot_errors:
                if err in r.text:
                    for i in range(3):
                        context.bot.send_message(text = f"REMINDER {DP[id][0]} HAS DUTY @ {HHMM}HRS", chat_id = duty_chat_id)
                        time.sleep(5)
                    context.bot.send_message(text = f"Call to {DP[id][0]} failed due to {err}.", chat_id = admin_id)
                    

        elif response == "ALRT": # DP Unable to show up for duty
            new_message = _generate_reminder_msg(Num, Name, Type, HHMM, f"ANYONE COVER {Name}?")
        update.effective_message.edit_text(text = "<pre>" + new_message + "</pre>", parse_mode = "HTML")


