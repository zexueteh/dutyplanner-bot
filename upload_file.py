import csv, requests, os, json
from dotenv import load_dotenv
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from read_data import _get_duty_message

def _write_file(file_name, file_data):
    with open(file_name, encoding = "utf-8-sig", mode = "w", newline = "") as file:
        writer = csv.writer(file)
        writer.writerows(file_data)

def _add_user(user):
    # Updates id <-> [name, username/HP] key-value pairs and returns updated dict

    with open("DP_usernames.json") as file:
        DP = json.load(file) 

    DP.update({str(user.id): [user.first_name, user.username if user.username else "NO USERNAME - INPUT NUMBER"]})

    with open("DP_usernames.json", "w") as file:
        json.dump(DP, file)
    return DP
            


def upload_function(update, context):
    # This message receives a duty forecast as mm_yyyy.csv (take note of naming convention) and saves it locally

    #step 1: Get metadata on file as a json object
    token, id, file_name = os.environ.get("my_token"), update.message.document.file_id, update.message.document.file_name
    metadata = requests.get(f"https://api.telegram.org/bot{token}/getFile?file_id={id}").json()
    
    #step 2: Using file path data in metadata, save in forecasts folder
    path = metadata["result"]["file_path"]
    file = requests.get(f"https://api.telegram.org/file/bot{token}/{path}")
    open(f"forecasts/{file_name}", "wb").write(file.content)

    context.bot.send_message(chat_id = update.effective_chat.id, text = f"File {file_name} has been saved.")






    





