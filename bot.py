import asyncio
import json
import logging
import os
import random
from datetime import datetime

from telegram import Bot

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sdmsmmpanel")
MIN_HOURS = float(os.getenv("MIN_HOURS", "2"))
MAX_HOURS = float(os.getenv("MAX_HOURS", "3"))
POSTS_FILE = os.getenv("POSTS_FILE", "posts.json")

DEFAULT_POSTS = [
    {
        "text": "🚀 BOOST YOUR SOCIAL MEDIA\n\nInstagram • TikTok • YouTube • Facebook\n\n✅ Followers\n✅ Likes\n✅ Views\n✅ Subscribers\n\nFast • Cheap • Reliable\n\n💎 SDM SMM PANEL\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    },
    {
        "text": "🔥 Grow your social presence with SDM SMM Panel\n\nGet high quality services for:\n• Instagram\n• TikTok\n• YouTube\n• Facebook\n• OTT & Premium Apps\n\n✅ Fast Delivery\n✅ Affordable Rates\n✅ Trusted Service\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    },
    {
        "text": "📈 Need more engagement?\n\nWe provide:\n• Followers\n• Likes\n• Views\n• Subscribers\n• Watchtime\n• Premium app services\n\nOrder now from SDM SMM Panel\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    },
    {
        "text": "⚡ Fast. Cheap. Reliable.\n\nYour one-stop hub for all SMM panel services.\n\n💎 SDM SMM PANEL\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    },
    {
        "text": "🎯 Want to boost your brand or page?\n\nSDM SMM Panel helps creators, businesses and influencers grow faster.\n\n🌐 Website: https://sdmpanel.co.in\n📢 Telegram: t.me/sdmsmmpanel"
    },
    {
        "text": "🔥 Daily deals available on SDM SMM Panel\n\nGrow on Instagram, TikTok, YouTube and Facebook with trusted services.\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    }
]


def ensure_posts_file():
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_POSTS, f, ensure_ascii=False, indent=2)
        logger.info("Created default posts.json")


def load_posts():
    ensure_posts_file()
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    if not isinstance(posts, list) or not posts:
        raise ValueError("posts.json must contain a non-empty JSON list.")

    cleaned = []
    for item in posts:
        if isinstance(item, dict) and item.get("text", "").strip():
            cleaned.append({"text": item["text"].strip()})

    if not cleaned:
        raise ValueError("posts.json has no valid posts.")

    return cleaned


async def send_post(bot: Bot, text: str):
    await bot.send_message(chat_id=CHANNEL_ID, text=text)
    logger.info("Posted successfully at %s", datetime.now().isoformat())


async def scheduler():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Add it in Railway Variables.")

    if MIN_HOURS <= 0 or MAX_HOURS <= 0 or MIN_HOURS > MAX_HOURS:
        raise ValueError("Check MIN_HOURS and MAX_HOURS env values.")

    bot = Bot(token=BOT_TOKEN)
    posts = load_posts()
    used_indexes = []

    logger.info("Bot started for channel: %s", CHANNEL_ID)
    logger.info("Posting interval: %s to %s hours", MIN_HOURS, MAX_HOURS)

    while True:
        try:
            posts = load_posts()

            available = [i for i in range(len(posts)) if i not in used_indexes]
            if not available:
                used_indexes = []
                available = list(range(len(posts)))

            idx = random.choice(available)
            used_indexes.append(idx)

            await send_post(bot, posts[idx]["text"])

        except Exception as e:
            logger.exception("Error while posting: %s", e)

        wait_hours = random.uniform(MIN_HOURS, MAX_HOURS)
        wait_seconds = int(wait_hours * 3600)
        logger.info("Next post in %.2f hours", wait_hours)
        await asyncio.sleep(wait_seconds)


if __name__ == "__main__":
    asyncio.run(scheduler())
