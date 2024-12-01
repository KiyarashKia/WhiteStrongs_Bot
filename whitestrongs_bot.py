import requests
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
import sys
from flask import Flask
import threading
import nest_asyncio  # Fix for nested event loop issue

# Apply nest_asyncio
nest_asyncio.apply()

# Add `libs` to system path
sys.path.insert(0, "libs")

# API and Bot Configuration
API_KEY = "6a3d20782bmsh74bb0e39633d701p1e82f2jsnf2647fda28bd"
BOT_TOKEN = "8061695627:AAHGAo4SUZsZFcAWH_MPc8P0jDMMq-LTixA"
CHANNEL_ID = "@TestWSbotter"
HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

# Flask keep-alive
app = Flask("")


@app.route("/")
def home():
    return "Bot is running!"


def run():
    app.run(host="0.0.0.0", port=8080)


threading.Thread(target=run).start()

# Farsi Team Names
TEAM_NAMES_FARSI = {
    "Real Madrid": "رئال مادرید",
    "Barcelona": "بارسلونا",
    "Atlético Madrid": "اتلتیکو مادرید",
    # Add other teams as necessary
}

# Global variables for live updates
is_live_update_running = False
sent_events = set()  # Track already sent events


# Fetch Events for a Given Fixture
def fetch_events(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/events?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code == 200:
        events = response.json()["response"]
        print(f"Fetched events: {events}")  # Debugging log
        return events
    else:
        print(f"Error fetching events: {response.status_code}")
        return []


# Format Events into Farsi Messages
def format_event_farsi(event):
    time = event["time"]["elapsed"]
    team = event["team"]["name"]
    player = event["player"]["name"]
    event_type = event["type"]
    detail = event["detail"]

    # Translate team name to Farsi
    team_farsi = TEAM_NAMES_FARSI.get(team, team)

    # Translate card type
    if detail == "Yellow Card":
        detail_farsi = "کارت زرد"
    elif detail == "Red Card":
        detail_farsi = "کارت قرمز"
    else:
        detail_farsi = detail

    if event_type == "Goal":
        return f"گل برای {team_farsi} در دقیقه {time} توسط {player}"
    elif event_type == "Card":
        return f"کارت {detail_farsi} برای {player} از تیم {team_farsi} در دقیقه {time}"
    elif event_type == "subst":
        return f"تعویض برای {team_farsi}: {player} وارد بازی شد در دقیقه {time}"
    else:
        return f"رویداد دیگر ({event_type}) برای {team_farsi} در دقیقه {time}"


# Fetch Ongoing Game Fixture ID
def fetch_live_fixture(team_id=40):  # Default is Real Madrid
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
        print("Checking for new events...")  # Debugging log
        events = fetch_events(fixture_id)

        for event in events:
            # Generate a unique key for each event using multiple attributes
            event_key = f"{event['time']['elapsed']}_{event['team']['name']}_{event['type']}_{event.get('player', {}).get('name', '')}"
            if event_key not in sent_events:  # Check if the event is new
                sent_events.add(event_key)  # Mark the event as sent
                message = format_event_farsi(event)
                print(f"Sending message: {message}")  # Debugging log
                await context.bot.send_message(chat_id=CHANNEL_ID,
                                               text=message)

        await asyncio.sleep(30)  # Wait for 30 seconds before checking again


# Telegram Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "خوش آمدید! شما می‌توانید از دستورات /live و /stop استفاده کنید.")


# Telegram Command: /live
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


# Telegram Command: /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_live_update_running
    if not is_live_update_running:
        await update.message.reply_text("هیچ آپدیت زنده‌ای در حال اجرا نیست.")
        return

    is_live_update_running = False
    await update.message.reply_text("آپدیت زنده متوقف شد.")


# Main Bot Setup
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("live", live))
    application.add_handler(CommandHandler("stop", stop))

    # Run the bot
    await application.run_polling()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
