import asyncio
import json
import logging
import os
import random
from datetime import datetime, time

from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sdmsmmpanel")
GROUP_ID = os.getenv("GROUP_ID", "@sdmsmmpanelchat")
POSTS_FILE = "posts.json"
BANNERS_FOLDER = "banners"

BEST_TIMES = [
    time(9, 0),
    time(12, 0),
    time(15, 0),
    time(18, 0),
    time(21, 0),
]

AUTO_REPLIES = {
    "price": "💰 You can check all service prices here:\nhttps://sdmpanel.co.in",
    "panel": "🚀 Order from SDM SMM Panel:\nhttps://sdmpanel.co.in",
    "followers": "📈 Boost followers instantly using SDM SMM Panel\nhttps://sdmpanel.co.in",
    "website": "🌐 Our official website:\nhttps://sdmpanel.co.in",
}

DEFAULT_POSTS = [
    "🚀 BOOST YOUR SOCIAL MEDIA\n\nInstagram • TikTok • YouTube • Facebook\n\nFollowers • Likes • Views • Subscribers\n\nFast • Cheap • Reliable\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel",
    "🔥 Grow faster with SDM SMM Panel\n\nBest services for creators & influencers\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel",
    "📈 Need more followers, likes and views?\n\nOrder now from SDM SMM Panel\n\n🌐 https://sdmpanel.co.in",
]


def load_posts():
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "w") as f:
            json.dump(DEFAULT_POSTS, f)
        return DEFAULT_POSTS

    with open(POSTS_FILE) as f:
        return json.load(f)


async def autopost(app: Application):
    await app.bot.initialize()

    while True:
        now = datetime.now().time()

        for post_time in BEST_TIMES:
            if abs(now.hour - post_time.hour) <= 0 and now.minute == post_time.minute:
                posts = load_posts()
                text = random.choice(posts)

                banner_path = None
                if os.path.exists(BANNERS_FOLDER):
                    banners = os.listdir(BANNERS_FOLDER)
                    if banners:
                        banner_path = os.path.join(
                            BANNERS_FOLDER, random.choice(banners)
                        )

                if banner_path:
                    with open(banner_path, "rb") as img:
                        await app.bot.send_photo(
                            chat_id=CHANNEL_ID,
                            photo=img,
                            caption=text,
                        )
                else:
                    await app.bot.send_message(CHANNEL_ID, text)

                logging.info("Posted scheduled promotion")

        await asyncio.sleep(60)


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("Usage: /post your message")
        return

    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)

    await update.message.reply_text("✅ Post sent to channel")


async def banner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to an image with /banner")
        return

    photo = update.message.reply_to_message.photo[-1]

    os.makedirs(BANNERS_FOLDER, exist_ok=True)

    file = await photo.get_file()

    filename = f"{BANNERS_FOLDER}/banner_{datetime.now().timestamp()}.jpg"

    await file.download_to_drive(filename)

    await update.message.reply_text("✅ Banner saved for autopost")


async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    text = update.message.text.lower()

    for key in AUTO_REPLIES:
        if key in text:
            await update.message.reply_text(AUTO_REPLIES[key])
            return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 SDM Panel Bot Active\n\nCommands:\n/post message\n/banner"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("banner", banner_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    loop = asyncio.get_event_loop()
    loop.create_task(autopost(app))

    app.run_polling()


if __name__ == "__main__":
    main()
