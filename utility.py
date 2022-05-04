from selenium import webdriver
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
import time, requests, json, os
from dotenv import load_dotenv

from upload_file import _add_user

load_dotenv()
admin_id = int(os.environ.get("admin_id"))


def welcome_function(update, context):
    new_member = update.message.new_chat_members[0]
    _add_user(new_member)

    welcome_msg = f"Hi {new_member.first_name}, Welcome to the HRSD duty group.\nDuty choosing and reminders are conducted here.\nPlease follow this link to authorize duty reminder calls:"

    context.bot.send_message(chat_id = update.effective_chat.id, text = "<pre>" + welcome_msg + "</pre>", parse_mode = "HTML")
    context.bot.send_message(chat_id = update.effective_chat.id, text = "https://api2.callmebot.com/txt/auth.php")

def leave_function(update, context):
    left_member = update.message.left_chat_members
    DP = _add_user(left_member)
    DP.pop(left_member.id)
    with open("DP_usernames.json", "w") as file:
        json.dump(DP, file)
    context.bot.send_message(chat_id = admin_id, text = f"<pre>{left_member.first_name} has been removed from JSON file.</pre>", parse_mode = "HTML")

def start_function(update, context):
    chat = update.effective_chat
    print(chat.id)
    msg = f"<pre>Duty Bot started for {update.effective_user.username}</pre>"
    # if chat.type == "group":
    #     msg = "Duty Bot Started"
    # elif chat.type == "private":
    #     msg = f"Duty Bot started for {update.effective_user.username}"
    


def help_function(update, context):
    pass

def call_function(update, context):
    username = str(context.args[0])
    message = "%20".join(context.args[1:])
    web_api = f"http://api.callmebot.com/start.php?source=auth&user=@{username}&text={message}&lang=en-IN-Standard-B"
    print(web_api)

    r = requests.get(web_api)
    print(r.text)
    #browser = webdriver.Firefox(executable_path = r"C:\Users\zexue\Downloads\geckodriver.exe")
    #browser = webdriver.Edge(executable_path=r"msedgedriver.exe") #C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
    #browser.get(web_api)
