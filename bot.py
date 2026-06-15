import os
import logging
import datetime
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# This pulls your token secretly from the cloud settings later
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Subject database mapped from Screenshot 2026-06-16 at 12.29.08 AM.jpg
SUBJECTS = {
    "CST-4104": {"name": "Artificial Intelligence", "lecturer": "Dr. Ei Moh Moh Aung"},
    "CST-4204": {"name": "Linear Algebra", "lecturer": "Dr. Sandar Win"},
    "CST-4306": {"name": "Management Principles and Engineering Economics", "lecturer": "Daw Khin Ei Ei Chaw"},
    "CST-4404": {"name": "Network Design and Engineering", "lecturer": "Dr. Ei Thin Su"},
    "CST-4405": {"name": "Computer Architecture and Organization", "lecturer": "Daw Hnin Pwint Zaw"},
    "CST-4503": {"name": "IELTS Academic Skills and Strategies", "lecturer": "U Kyi Win"},
    "CST-4105": {"name": "Enterprise Applications Development using Java (Keystone Project)", "lecturer": "Dr. Ei Moh Moh Aung"},
    "CST-4307": {"name": "Advanced Web Technology with PHP (Keystone Project)", "lecturer": "Dr. Lei Yi Win Iwin"},
    "CST-4406": {"name": "Data and Computer Communications", "lecturer": "Daw Akari Myint Soe"},
    "CST-4407": {"name": "Engineering Circuits", "lecturer": "Dr. Thiri Thitsar Khaing"},
    "CST-4408": {"name": "Foundations of Cybersecurity", "lecturer": "Dr. Aung Htein Maw"},
}

# Day-by-day structural schedule from Screenshot 2026-06-16 at 12.29.08 AM.jpg
SCHEDULE = {
    "Monday": [
        {"time": "08:30 - 09:30", "code": "CST-4204", "type": "TDA", "room": "425"},
        {"time": "09:40 - 10:40", "code": "CST-4405", "type": "TDA", "room": "425"},
        {"time": "10:50 - 11:50", "code": "CST-4306", "type": "TDA", "room": "424"},
        {"time": "11:50 - 12:40", "is_break": True},
        {"time": "12:40 - 01:40", "code": "CST-4404", "type": "L", "room": "326"},
        {"time": "01:50 - 02:50", "code": "CST-4503", "type": "L", "room": "326"},
        {"time": "03:00 - 04:00", "code": "CST-4104", "type": "L", "room": "326"},
    ],
    "Tuesday": [
        {"time": "08:30 - 09:30", "is_elective": True, "type": "TDA", "rooms": {"CST-4105": "231", "CST-4307": "233", "CST-4406": "433", "CST-4407": "434", "CST-4408": "421"}},
        {"time": "09:40 - 10:40", "code": "CST-4404", "type": "TDA", "room": "233"},
        {"time": "10:50 - 11:50", "code": "CST-4405", "type": "TDA", "room": "235"},
        {"time": "11:50 - 12:40", "is_break": True},
        {"time": "12:40 - 01:40", "code": "CST-4204", "type": "L", "room": "326"},
        {"time": "01:50 - 02:50", "code": "CST-4104", "type": "L", "room": "326"},
        {"time": "03:00 - 04:00", "code": "CST-4306", "type": "L", "room": "326"},
    ],
    "Wednesday": [
        {"time": "08:30 - 09:30", "no_class": True},
        {"time": "09:40 - 10:40", "code": "CST-4104", "type": "TDA", "room": "424"},
        {"time": "10:50 - 11:50", "code": "CST-4204", "type": "TDA", "room": "424"},
        {"time": "11:50 - 12:40", "is_break": True},
        {"time": "12:40 - 01:40", "code": "CST-4503", "type": "TDA", "room": "432"},
        {"time": "01:50 - 02:50", "is_elective": True, "type": "TDA", "rooms": {"CST-4105": "232", "CST-4307": "231", "CST-4406": "433", "CST-4407": "434", "CST-4408": "421"}},
        {"time": "03:00 - 04:00", "no_class": True},
    ],
    "Thursday": [
        {"time": "08:30 - 09:30", "code": "CST-4104", "type": "TDA", "room": "424"},
        {"time": "09:40 - 10:40", "code": "CST-4306", "type": "TDA", "room": "424"},
        {"time": "10:50 - 11:50", "code": "CST-4503", "type": "L", "room": "334"},
        {"time": "11:50 - 12:40", "is_break": True},
        {"time": "12:40 - 01:40", "code": "CST-4404", "type": "L", "room": "326"},
        {"time": "01:50 - 02:50", "code": "CST-4405", "type": "L", "room": "326"},
        {"time": "03:00 - 04:00", "code": "CST-4204", "type": "L", "room": "326"},
    ],
    "Friday": [
        {"time": "08:30 - 09:30", "is_elective": True, "type": "L", "rooms": {"CST-4105": "235", "CST-4307": "233", "CST-4406": "433", "CST-4407": "434", "CST-4408": "421"}},
        {"time": "09:40 - 10:40", "code": "CST-4503", "type": "TDA", "room": "244 (E-Lab)"},
        {"time": "10:50 - 11:50", "code": "CST-4404", "type": "TDA", "room": "425"},
        {"time": "11:50 - 12:40", "is_break": True},
        {"time": "12:40 - 01:40", "code": "CST-4306", "type": "L", "room": "326"},
        {"time": "01:50 - 02:50", "code": "CST-4405", "type": "L", "room": "326"},
        {"time": "03:00 - 04:00", "is_elective": True, "type": "L", "rooms": {"CST-4105": "233", "CST-4307": "232", "CST-4406": "334", "CST-4407": "335", "CST-4408": "336"}},
    ]
}

def generate_schedule_text(day: str) -> str:
    if day not in SCHEDULE:
        return f"📅 *{day}*\n\nNo classes scheduled! Enjoy your weekend. 🎉"
    
    output = f"📅 *Class Schedule for {day}*:\n\n"
    output += "—" * 15 + "\n\n"
    
    for session in SCHEDULE[day]:
        time_slot = session["time"]
        if session.get("is_break"):
            output += f"☕ *{time_slot}* — **BREAK**\n\n"
        elif session.get("no_class"):
            output += f"⚪ *{time_slot}* — *Free Period (No Class)*\n\n"
        elif session.get("is_elective"):
            output += f"📘 *{time_slot}* | **Elective Tracks ({session['type']})**\n"
            for code, room in session["rooms"].items():
                sub_info = SUBJECTS.get(code, {"name": "Unknown Sub", "lecturer": "Unknown"})
                output += f"  • *{code}*: {sub_info['name']}\n    📍 Room: {room} | 👤 {sub_info['lecturer']}\n"
            output += "\n"
        else:
            code = session["code"]
            stype = session["type"]
            room = session["room"]
            sub_info = SUBJECTS.get(code, {"name": "Unknown Sub", "lecturer": "Unknown"})
            output += f"📕 *{time_slot}* | **{code} ({stype})**\n  📚 _Subject:_ {sub_info['name']}\n  📍 _Room:_ {room}\n  👤 _Lecturer:_ {sub_info['lecturer']}\n\n"
            
    return output

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["Today"], ["Monday", "Tuesday", "Wednesday"], ["Thursday", "Friday"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 **Welcome to your Academic Timetable Bot!**\n\nUse the options panel below to view your schedule details automatically.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selection = update.message.text
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    if selection == "Today":
        current_day = datetime.datetime.now().strftime("%A")
        response_text = generate_schedule_text(current_day)
    elif selection in valid_days:
        response_text = generate_schedule_text(selection)
    else:
        response_text = "🤖 Please select an option using the on-screen menu layout."

    await update.message.reply_text(response_text, parse_mode="Markdown")

def main():
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection))
    
    print("🤖 Timetable bot is live online!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()