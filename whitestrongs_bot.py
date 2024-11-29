import requests
import asyncio
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, InlineQueryHandler
from uuid import uuid4
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

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Welcome! Use the inline mode by typing @<bot_username> and choosing `/prev` or `/live`. "
        "Or use the commands directly: `/prev` and `/live`."
    )

# Command: /prev
async def prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is the result of the /prev command!")

# Command: /live
async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is the result of the /live command!")

# Inline Query Handler
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = []

    if query == "/prev":
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Previous Results",
                input_message_content=InputTextMessageContent("This is the result of /prev command!")
            )
        )
    elif query == "/live":
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Live Updates",
                input_message_content=InputTextMessageContent("This is the result of /live command!")
            )
        )
    else:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Default Response",
                input_message_content=InputTextMessageContent("Use `/prev` or `/live` in inline queries.")
            )
        )

    await context.bot.answer_inline_query(update.inline_query.id, results)

# Main Bot Setup
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prev", prev))
    application.add_handler(CommandHandler("live", live))
    application.add_handler(InlineQueryHandler(inline_query))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
