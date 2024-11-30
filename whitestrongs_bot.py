import requests
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
import sys
from flask import Flask
import threading
import nest_asyncio

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

# Bot running status
bot_running = True


@app.route("/")
def home():
    if bot_running:
        return "⚡ Bot is running!", 200
    else:
        return "❌ Bot is not running!", 503


def run():
    app.run(host="0.0.0.0", port=8080)


threading.Thread(target=run).start()

# Farsi Team Names
TEAM_NAMES_FARSI = {
    "Arsenal": "آرسنال",
    "Aston Villa": "استون ویلا",
    "Liverpool": "لیورپول",
    "Manchester City": "منچستر سیتی",
    "Atlético Madrid": "اتلتیکو مادرید",
    "Barcelona": "بارسلونا",
    "Girona": "خیرونا",
    "Real Madrid": "رئال مادرید",
    "Atalanta": "آتالانتا",
    "Bologna": "بولونیا",
    "Inter Milan": "اینتر میلان",
    "Juventus": "یوونتوس",
    "Milan": "آث میلان",
    "Bayern Munich": "بایرن مونیخ",
    "Borussia Dortmund": "بوروسیا دورتموند",
    "RB Leipzig": "لایپزیگ",
    "Stuttgart": "اشتوتگارت",
    "Brest": "برست",
    "Lille": "لیل",
    "Monaco": "موناکو",
    "Paris Saint-Germain": "پاری سن ژرمن",
    "Benfica": "بنفیکا",
    "Sporting CP": "اسپورتینگ لیسبون",
    "Feyenoord": "فاینورد",
    "PSV Eindhoven": "پی‌اس‌وی آیندهوون",
    "Celtic": "سلتیک",
    "Club Brugge": "کلاب بروژ",
    "Dinamo Zagreb": "دینامو زاگرب",
    "Red Bull Salzburg": "ردبول زالتسبورگ",
    "Sturm Graz": "اشتورم گراتس",
    "Red Star Belgrade": "ستاره سرخ بلگراد",
    "Shakhtar Donetsk": "شاختار دونتسک",
    "Sparta Prague": "اسپارتا پراگ",
    "Slovan Bratislava": "اسلووان براتیسلاوا",
    "Young Boys": "یانگ بویز",
    "Athletic Club": "اتلتیک بیلبائو",
    "CA Osasuna": "اوساسونا",
    "CD Leganés": "لگانس",
    "Deportivo Alavés": "آلاوز",
    "Getafe CF": "ختافه",
    "Rayo Vallecano": "رایو وایکانو",
    "RC Celta": "سلتاویگو",
    "RCD Espanyol de Barcelona": "اسپانیول بارسلونا",
    "RCD Mallorca": "مایورکا",
    "Real Betis": "رئال بتیس",
    "Real Sociedad": "رئال سوسیداد",
    "Real Valladolid CF": "رئال وایادولید",
    "Sevilla FC": "سویا",
    "UD Las Palmas": "لاس پالماس",
    "Valencia CF": "والنسیا",
    "Villarreal CF": "ویارئال",
}


# Fetch Events for a Given Fixture
def fetch_events(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/events?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        print("Error fetching events:", response.status_code)
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
        detail_farsi = "کارت زرد ⚠️"
    elif detail == "Red Card":
        detail_farsi = "کارت قرمز 🟥"
    else:
        detail_farsi = detail

    if event_type == "Goal":
        return f"⚽ گل برای {team_farsi} در دقیقه {time} توسط {player} 🎉"
    elif event_type == "Card":
        return f"🃏 {detail_farsi} برای {player} از تیم {team_farsi} در دقیقه {time}"
    elif event_type == "subst":
        return f"🔄 تعویض برای {team_farsi}: {player} از بازی خارج شد در دقیقه {time}"
    else:
        return f"📋 رویداد دیگر ({event_type}) برای {team_farsi} در دقیقه {time}"


# Fetch Previous Game Fixture ID
def fetch_previous_fixture(team_id=40):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?last=1&team={team_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["response"][0]["fixture"]["id"] if data[
            "response"] else None
    else:
        print("❌ Error fetching previous fixture:", response.status_code)
        return None


# Fetch Ongoing Game Fixture ID
def fetch_live_fixture(team_id=40):  # Default is Liverpool
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all&team={team_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data["response"]:
            return data["response"][0]["fixture"]["id"]
        else:
            return None
    else:
        print("❌ Error fetching live fixture:", response.status_code)
        return None


# Telegram Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 خوش آمدید!\n\n📋 دستورات قابل استفاده:\n"
                                    "- /prev: مشاهده رویدادهای مسابقه قبلی 🔙\n"
                                    "- /live: مشاهده رویدادهای مسابقه زنده 🔴")


# Telegram Command: Fetch Previous Game Events
async def prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fixture_id = fetch_previous_fixture()
    if not fixture_id:
        await update.message.reply_text("❌ خطا در یافتن مسابقه قبلی.")
        return

    events = fetch_events(fixture_id)
    if not events:
        await update.message.reply_text(
            "❌ هیچ رویدادی برای مسابقه قبلی یافت نشد.")
        return

    for event in events:
        message = format_event_farsi(event)
        await update.message.reply_text(message)


# Telegram Command: Fetch Live Game Events
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fixture_id = fetch_live_fixture()
    if not fixture_id:
        await update.message.reply_text(
            "❌ در حال حاضر هیچ مسابقه زنده‌ای یافت نشد.")
        return

    events = fetch_events(fixture_id)
    if not events:
        await update.message.reply_text(
            "❌ هیچ رویدادی برای مسابقه زنده یافت نشد.")
        return

    for event in events:
        message = format_event_farsi(event)
        await update.message.reply_text(message)


# Main Bot Setup
async def main():
    global bot_running
    bot_running = True

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))  # No "/" in commands
    application.add_handler(CommandHandler("prev", prev))
    application.add_handler(CommandHandler("live", live))

    # Run the bot
    try:
        await application.run_polling()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        bot_running = False  # Set the bot as not running when exiting


if __name__ == "__main__":
    asyncio.run(main())
