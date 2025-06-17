import os
from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from pytz import timezone
import base64
import json


app = Flask(__name__, static_folder='static', template_folder='templates')

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_json = os.environ.get("GOOGLE_CREDS_JSON")
creds_dict = json.loads(base64.b64decode(creds_json).decode("utf-8"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("ExpenseTracker").sheet1

@app.route('/', methods=['GET', 'POST'])
def home():
    records = sheet.get_all_records()

    # Safely convert User to string for sorting
    users = sorted(set(str(row["User"]) for row in records if row["User"]))

    # Format timestamps
    for record in records:
        try:
            dt = datetime.strptime(record["Timestamp"], "%H:%M %d-%m-%Y")
            record["Timestamp"] = dt.strftime("%H:%M %d-%m-%Y")
        except:
            pass

    selected_user = request.form.get("user")
    filter_today = request.form.get("today") == "on"

    filtered_records = records
    if selected_user:
        filtered_records = [r for r in filtered_records if str(r["User"]) == selected_user]

    if filter_today:
        today_str = datetime.now(timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
        filtered_records = [r for r in filtered_records if today_str in r["Timestamp"]]

    return render_template("index.html", records=filtered_records, users=users,
                           selected_user=selected_user, filter_today=filter_today)

@app.route('/add', methods=['POST'])
def add():
    user = request.form['user']
    amount = request.form['amount']
    category = request.form['category']
    timestamp = datetime.now(timezone("Asia/Kolkata")).strftime("%H:%M %d-%m-%Y")

    sheet.append_row(["", timestamp, user, amount, category])  # Keep UserID empty
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)