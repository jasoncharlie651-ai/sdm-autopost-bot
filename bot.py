import asyncio
import json
import logging
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sdmsmmpanel")
WEBSITE_URL = "https://sdmpanel.co.in"

DATA_DIR = Path("data")
POSTS_FILE = DATA_DIR / "posts.json"
SCHEDULE_FILE = DATA_DIR / "schedule.json"

DATA_DIR.mkdir(exist_ok=True)

DEFAULT_POSTS = [
"🚀 BOOST YOUR SOCIAL MEDIA\n\nFollowers • Likes • Views • Subscribers\n\n🌐 https://sdmpanel.co.in",
"🔥 Grow faster using SDM SMM Panel\n\nBest SMM services available now\n\n🌐 https://sdmpanel.co.in",
"📈 Need more engagement?\n\nUse SDM SMM Panel today\n\n🌐 https://sdmpanel.co.in"
]


def load_json(path, default):
    if not path.exists():
        with open(path, "w") as f:
            json.dump(default, f)
        return default

    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_posts():
    return load_json(POSTS_FILE, DEFAULT_POSTS)


def load_schedule():
    return load_json(SCHEDULE_FILE, [])


async def autopost_loop(app: Application):
    await app.bot.initialize()

    while True:
        try:
            posts = load_posts()

            if not posts:
                await asyncio.sleep(600)
                continue

            post = random.choice(posts)

            await app.bot.send_message(CHANNEL_ID, post)

            wait_hours = random.randint(2, 3)

            await asyncio.sleep(wait_hours * 3600)

        except Exception as e:
            logging.error(e)
            await asyncio.sleep(300)
async def reseller(update, context):
    user_id = update.effective_user.id
    referral = f"https://t.me/sdmsmmpanel?start=ref{user_id}"

    text = f"""
💼 SDM PANEL RESELLER PROGRAM

Earn rewards by inviting users to SDM SMM Panel.

Your referral link:
{referral}

Share this link with your customers and audience.
When they join through your link, you can track them for reseller rewards.

🌐 https://sdmpanel.co.in
📢 https://t.me/sdmsmmpanel?direct
"""

    await update.message.reply_text(text)

async def scheduler_loop(app: Application):
    await app.bot.initialize()

    while True:
        try:
            schedule = load_schedule()
            now = datetime.utcnow()

            for item in schedule:
                post_time = datetime.fromisoformat(item["time"])

                if now >= post_time and not item.get("done"):
                    await app.bot.send_message(CHANNEL_ID, item["text"])

                    item["done"] = True

                    save_json(SCHEDULE_FILE, schedule)

            await asyncio.sleep(60)

        except Exception as e:
            logging.error(e)
            await asyncio.sleep(60)


async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("Usage: /addpost your message")
        return

    posts = load_posts()

    posts.append(text)

    save_json(POSTS_FILE, posts)

    await update.message.reply_text("✅ Post added to rotation list")


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = " ".join(context.args)

    if "|" not in raw:
        await update.message.reply_text("Usage: /schedule YYYY-MM-DD HH:MM | message")
        return

    time_str, text = raw.split("|", 1)

    try:
        post_time = datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M")
    except:
        await update.message.reply_text("Invalid time format")
        return

    schedule = load_schedule()

    schedule.append({
        "time": post_time.isoformat(),
        "text": text.strip(),
        "done": False
    })

    save_json(SCHEDULE_FILE, schedule)

    await update.message.reply_text("✅ Post scheduled")


async def listposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    posts = load_posts()

    msg = "\n\n".join(posts[:10])

    await update.message.reply_text("Current rotating posts:\n\n" + msg)


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ideas = [
        "🔥 Limited Time Offer on Instagram Followers",
        "⚡ Cheapest TikTok Views available now",
        "🚀 Boost your YouTube channel instantly",
        "💰 Discount available on SMM services today"
    ]

    text = random.choice(ideas) + "\n\nOrder now:\n" + WEBSITE_URL

    await update.message.reply_text(text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
"""
🤖 SDM PANEL BOT READY

Commands:

/addpost message
Add message to auto rotation

/schedule YYYY-MM-DD HH:MM | message
Schedule a post

/listposts
Show rotating messages

/generate
Generate promo post
"""
)


def main():

    if not BOT_TOKEN:
        raise Exception("BOT_TOKEN missing")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpost", addpost))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("listposts", listposts))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("reseller", reseller))
    loop = asyncio.get_event_loop()

    loop.create_task(autopost_loop(app))
    loop.create_task(scheduler_loop(app))

    app.run_polling()


if __name__ == "__main__":
    main()
