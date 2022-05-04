import csv, json
from datetime import datetime, date, timedelta
from prettytable import PrettyTable

month_dict = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
weekday_dict = {0:"MON", 1:"TUE", 2:"WED", 3:"THU", 4:"FRI", 5:"SAT", 6:"SUN"}

def _get_duty_message(mm, yyyy, comments = ""):
    header = f"DUTY FOR THE MONTH OF {month_dict[mm]} {yyyy}\n"

    # opening DP dictionary
    with open("DP_usernames.json") as file:
        DP_dict = json.load(file) 

    # Creating table and formatting columns to fit telegram messages
    table = PrettyTable(["DD","DAY","S", "STRT", "TY", "DP"])
    table.left_padding_width, table.right_padding_width = 0, 0
    table.align["DP"] = "l"

    # adding rows to table based on data from csv forcast
    with open(f"forecasts/{mm}_{yyyy}.csv", encoding = "utf-8-sig") as file:
        for row in csv.reader(file):
            weekday = weekday_dict[datetime(year = yyyy, month = mm, day = int(row[0])).weekday()]
            if len(row) == 4:
                table.add_row([row[0], weekday, row[1], row[2], row[3], ""])
            else:
                table.add_row([row[0], weekday, row[1], row[2], row[3], DP_dict[row[4]][0]])
    
    return "<pre>" + header + str(table) + "\n"+ comments + "</pre>"
    


