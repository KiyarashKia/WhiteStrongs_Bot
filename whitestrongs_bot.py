import requests
import asyncio
from telegram import Bot

# API and Bot Configuration
API_KEY = "6a3d20782bmsh74bb0e39633d701p1e82f2jsnf2647fda28bd"
BOT_TOKEN = "8061695627:AAHGAo4SUZsZFcAWH_MPc8P0jDMMq-LTixA"
CHANNEL_ID = "@TestWSbotter"
HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

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
    "Girona": "گیرونا",
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
    
    

# Send Message to Telegram Channel (Async)
async def send_to_telegram(message):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text=message)

# Main Fetch and Send Events
async def main():
    fixture_id = 1299071  # Real Madrid vs Any
    events = fetch_events(fixture_id)
    for event in events:
        message = format_event_farsi(event)
        send_to_telegram(message)

# Run the Bot
if __name__ == "__main__":
    main()
