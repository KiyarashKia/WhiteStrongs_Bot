import time
import requests
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
import sys
from flask import Flask
import threading
import nest_asyncio
import os
from dotenv import load_dotenv

REAL_MADRID_ID = 541

# Load environment variables from .env file
load_dotenv()

# Apply nest_asyncio
nest_asyncio.apply()

# Add `libs` to system path
sys.path.insert(0, "libs")

# API and Bot Configuration
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@TestWSbotter"
HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

# Flask keep-alive
app = Flask("")

# Global variables
is_live_update_running = False
sent_events = set()  # Track already sent events
bot_operational = False  # Track if the bot is operational


# Flask endpoint to check bot status
@app.route("/")
def home():
    global bot_operational
    if not bot_operational:
        return "❌ Bot is not running.", 503
    return "✅ Bot is running!", 200


def run():
    app.run(host="0.0.0.0", port=8080)


threading.Thread(target=run).start()

# Farsi Team Names
TEAM_NAMES_FARSI = {
    "Real Madrid": "رئال مادرید",
    "Barcelona": "بارسلونا",
    "Atlético Madrid": "اتلتیکو مادرید",
    "Sevilla": "سویا",
    "Villarreal": "ویارئال",
    "Real Sociedad": "رئال سوسیداد",
    "Athletic Club": "اتلتیک بیلبائو",
    "Betis": "رئال بتیس",
    "Celta Vigo": "سلتاویگو",
    "Valencia": "والنسیا",
    "Getafe": "ختافه",
    "Espanyol": "اسپانیول",
    "Osasuna": "اوساسونا",
    "Girona": "خیرونا",
    "Rayo Vallecano": "رایو وایکانو",
    "Mallorca": "مایورکا",
    "Alavés": "آلاوز",
    "Las Palmas": "لاس پالماس",
    "Liverpool": "لیورپول",
    "Manchester City": "منچستر سیتی",
    "Bayern München": "بایرن مونیخ",
    "PSG": "پاری سن ژرمن",
    "Juventus": "یوونتوس",
    "Inter": "اینترمیلان",
    "AC Milan": "آث میلان",
    "Borussia Dortmund": "دورتموند",
    "Benfica": "بنفیکا",
}

# Farsi Player Names 2024-25
PLAYER_NAMES_FARSI = {
    "T. Courtois": "تیبو کورتوا",
    "A. Lunin": "آندری لونین",
    "F. González": "فران گونزالس",
    "S. Mestre": "سرخیو مستره",
    "D. Carvajal": "دنی کارواخال",
    "É. Militão": "ادر میلیتائو",
    "D. Alaba": "داوید آلابا",
    "J. Vallejo": "خسوس وایخو",
    "F. García": "فران گارسیا",
    "A. Rüdiger": "آنتونیو رودیگر",
    "F. Mendy": "فرلاند مندی",
    "J. Ramón": "خاکوبو رامون",
    "R. Asencio": "رائول آسنسیو",
    "D. Jiménez": "داوید خیمنز",
    "L. Aguado": "لورنزو آگوادو",
    "D. Aguado": "دیه‌گو آگوادو",
    "J. Bellingham": "جود بلینگهام",
    "E. Camavinga": "ادواردو کاماوینگا",
    "F. Valverde": "فدریکو والورده",
    "L. Modric": "لوکا مودریچ",
    "A. Tchouaméni": "اوریلین شوامنی",
    "A. Güler": "آردا گولر",
    "L. Vázquez": "لوکاس وازکز",
    "D. Ceballos": "دنی سبایوس",
    "B. Díaz": "براهیم دیاز",
    "C. Andrés": "چما آندرس",
    "H. De Llanos": "هوگو دلانوس",
    "V. Júnior": "وینیسیوس جونیور",
    "K. Mbappé": "کیلیان امباپه",
    "Rodrygo": "رودریگو",
    "Endrick": "اندریک",
    "G. García": "گونزالو گارسیا",
    "D. Yáñez": "دنیل یانز"
}


# Fetch Events for a Given Fixture
def fetch_events(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/events?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        print(f"Error fetching events: {response.status_code}")
        return []


# Fetch Previous Game Fixture ID
def fetch_previous_fixture(team_id=541):  # Real Madrid
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?last=1&team={team_id}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json().get("response", [])
        return data[0]["fixture"]["id"] if data else None
    except requests.RequestException as e:
        print(f"Error fetching previous fixture: {e}")
        return None


# Format Events into Farsi Messages
def format_event_farsi(event):
    time = event["time"]["elapsed"]
    team_id = event["team"]["id"]
    team_name = event["team"]["name"]
    player = event.get("player", {}).get("name", "unknown")
    assist = event.get("assist", {}).get("name", None)  # For substitutions
    event_type = event["type"]
    detail = event["detail"]

    # Translate team and player names to Farsi
    team_farsi = TEAM_NAMES_FARSI.get(team_name, team_name)
    player_farsi = PLAYER_NAMES_FARSI.get(player, player)
    assist_farsi = PLAYER_NAMES_FARSI.get(assist, assist) if assist else None

    # Customize messages for goals
    if event_type == "Goal":
        if detail == "Normal Goal":
            if team_id == REAL_MADRID_ID:  # If Real Madrid scores
                return f"گللللللللللللل 🎉🎉🎉🎉 ! {player_farsi} در دقیقه {time}!"
            else:  # If opponent scores
                return f"گل برای {team_farsi} در دقیقه {time} توسط {player_farsi}"
        elif detail == "Missed Penalty":
            return f"پنالتی برای {player_farsi} از تیم {team_farsi} از دست رفت در دقیقه {time}!"

    # Translate card type
    # if detail == "Yellow Card":
    #     detail_farsi = "کارت زرد"
    # elif detail == "Red Card":
    #     detail_farsi = "کارت قرمز"
    # else:
    #     detail_farsi = detail

# Handle cards
    if event_type == "Card":
        detail_farsi = "زرد 🟨" if detail == "Yellow Card" else "قرمز 🟥" if detail == "Red Card" else detail
        return f"کارت {detail_farsi} برای {player_farsi} از تیم {team_farsi} در دقیقه {time}"

# Handle substitutions
    elif event_type == "subst":
        if assist_farsi:  # Include outgoing player if available
            return f"تعویض برای {team_farsi} در دقیقه {time}:\n{player_farsi} 🟢\n{assist_farsi} 🔴"
        else:  # No outgoing player specified
            return f"تعویض برای {team_farsi}: {player_farsi} وارد بازی شد در دقیقه {time}"

    # Handle other events
    else:
        return f"رویداد دیگر ({event_type}) برای {team_farsi} در دقیقه {time}"


# Fetch Ongoing Game Fixture ID
def fetch_live_fixture(team_id=REAL_MADRID_ID):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all&team={team_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data["response"]:
            fixture_id = data["response"][0]["fixture"]["id"]
            print(f"Live fixture found: {fixture_id}")  # Debugging log
            return fixture_id
        else:
            print("No live games found.")
            return None
    else:
        print(f"Error fetching live fixture: {response.status_code}")
        return None


# Function to send live updates periodically
async def send_live_updates(context: ContextTypes.DEFAULT_TYPE,
                            fixture_id: int):
    global is_live_update_running, sent_events
    is_live_update_running = True

    while is_live_update_running:
        events = fetch_events(fixture_id)

        for event in events:
            # Generate a unique key for each event
            event_key = f"{event['time']['elapsed']}_{event.get('team', {}).get('id', '')}_{event['type']}_{event['detail']}_{event.get('player', {}).get('id', '')}_{event.get('assist', {}).get('id', '')}"

            # Check if the event has already been processed
            if event_key in sent_events:
                continue  # Skip already processed events

            # Check if the event data is incomplete (e.g., unknown player)
            if not event.get("player", {}).get("name"):
                # Retry after 5 seconds if player is unknown
                print(
                    f"Incomplete event detected, retrying in 5 seconds: {event}"
                )
                await asyncio.sleep(5)
                continue  # Skip processing for now and wait for the next cycle

            # Mark the event as sent and process it
            sent_events.add(event_key)
            message = format_event_farsi(event)
            await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

        await asyncio.sleep(70)  # Adjusted fetching interval


# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_operational
    bot_operational = True  # Set bot as operational when it starts
    await update.message.reply_text(
        "خوش آمدید! شما می‌توانید از دستورات /live و /stop استفاده کنید.")


# Command: /live
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_live_update_running, sent_events

    if is_live_update_running:
        await update.message.reply_text("آپدیت زنده از قبل در حال اجرا است.")
        return

    fixture_id = fetch_live_fixture()
    if not fixture_id:
        await update.message.reply_text(
            "در حال حاضر هیچ مسابقه زنده‌ای یافت نشد.")
        return

    sent_events.clear()  # Clear previously sent events for a new live session
    await update.message.reply_text("آپدیت زنده شروع شد.")
    asyncio.create_task(send_live_updates(context, fixture_id))


# Command: /prev
async def prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch the previous fixture ID
    fixture_id = fetch_previous_fixture()
    if not fixture_id:
        await update.message.reply_text(
            "هیچ بازی قبلی پیدا نشد. لطفاً مطمئن شوید تیم بازی کرده است.")
        return

    # Fetch events for the previous fixture
    events = fetch_events(fixture_id)
    if not events:
        await update.message.reply_text("هیچ رویدادی برای بازی قبلی یافت نشد.")
        return

    # Format and send all events
    messages = []
    for event in events:
        formatted_event = format_event_farsi(event)
        messages.append(formatted_event)

    # Send all messages (split to avoid Telegram's message length limit)
    for message in messages:
        await update.message.reply_text(message)


# Command: /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_live_update_running
    if not is_live_update_running:
        await update.message.reply_text("هیچ آپدیت زنده‌ای در حال اجرا نیست.")
        return

    is_live_update_running = False
    await update.message.reply_text("آپدیت زنده متوقف شد.")


# Main Bot Setup
async def main():
    global bot_operational
    bot_operational = True  # Mark bot as operational when the bot is running

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("live", live))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("prev", prev))

    # Run the bot
    try:
        await application.run_polling()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        bot_operational = False  # Set to False if the bot stops


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
