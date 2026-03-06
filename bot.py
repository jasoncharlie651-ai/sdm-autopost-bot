import asyncio
import json
import logging
import os
import random
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.constants import ChatAction
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
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sdmsmmpanel")
GROUP_ID = os.getenv("GROUP_ID", "@sdmsmmpanelchat")
ADMIN_USER_IDS = {
    int(x.strip())
    for x in os.getenv("ADMIN_USER_IDS", "").split(",")
    if x.strip().isdigit()
}
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://sdmpanel.co.in")
WEBSITE_ORDER_API = os.getenv("WEBSITE_ORDER_API", "")
WEBSITE_API_KEY = os.getenv("WEBSITE_API_KEY", "")
MIN_POST_GAP_MINUTES = int(os.getenv("MIN_POST_GAP_MINUTES", "120"))
MAX_POST_GAP_MINUTES = int(os.getenv("MAX_POST_GAP_MINUTES", "180"))
TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", "5"))

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
POSTS_FILE = DATA_DIR / "posts.json"
DEALS_FILE = DATA_DIR / "deals.json"
ORDERS_FILE = DATA_DIR / "orders.json"
BANNERS_DIR = DATA_DIR / "banners"
GENERATED_DIR = DATA_DIR / "generated"
ASSETS_DIR = Path(os.getenv("ASSETS_DIR", "assets"))
LOGO_PATH = Path(os.getenv("LOGO_PATH", str(ASSETS_DIR / "logo.png")))
BACKGROUND_PATH = Path(os.getenv("BACKGROUND_PATH", str(ASSETS_DIR / "banner_bg.png")))
FONT_PATH = os.getenv("FONT_PATH", "")

DEFAULT_POSTS = [
    {
        "type": "promo",
        "text": "🚀 BOOST YOUR SOCIAL MEDIA\n\nInstagram • TikTok • YouTube • Facebook\n\nFollowers • Likes • Views • Subscribers\n\nFast • Cheap • Reliable\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    },
    {
        "type": "promo",
        "text": "🔥 Grow faster with SDM SMM Panel\n\nHigh quality SMM services for creators, influencers and businesses.\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    },
    {
        "type": "promo",
        "text": "📈 Need more followers, likes and views?\n\nOrder from SDM SMM Panel today.\n\n🌐 https://sdmpanel.co.in\n📢 t.me/sdmsmmpanel"
    }
]

DEFAULT_DEALS = [
    {
        "title": "Instagram Flash Deal",
        "price": "Starting from ₹49",
        "details": "Followers • Likes • Views",
        "cta": "Order now at https://sdmpanel.co.in"
    },
    {
        "title": "YouTube Growth Offer",
        "price": "Starting from ₹99",
        "details": "Subscribers • Watchtime • Views",
        "cta": "Visit https://sdmpanel.co.in"
    },
    {
        "title": "OTT & Premium Apps",
        "price": "Best daily deals available",
        "details": "Premium app subscriptions and digital services",
        "cta": "Check latest offers at https://sdmpanel.co.in"
    }
]

AUTO_REPLIES = {
    "price": "💰 Latest rates and services are available on our website:\nhttps://sdmpanel.co.in",
    "panel": "🚀 Order directly from SDM SMM Panel:\nhttps://sdmpanel.co.in",
    "followers": "📈 Boost followers instantly with SDM SMM Panel\nhttps://sdmpanel.co.in",
    "website": "🌐 Official website:\nhttps://sdmpanel.co.in",
    "order": "🛒 You can place your order here:\nhttps://sdmpanel.co.in",
    "discount": "💰 Today deals are shared regularly in the channel. Also check:\nhttps://sdmpanel.co.in",
}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BANNERS_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_json(path: Path, default_data):
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_posts():
    posts = ensure_json(POSTS_FILE, DEFAULT_POSTS)
    return [p for p in posts if isinstance(p, dict) and p.get("text")]


def load_deals():
    deals = ensure_json(DEALS_FILE, DEFAULT_DEALS)
    return [d for d in deals if isinstance(d, dict) and d.get("title")]


def load_orders():
    return ensure_json(ORDERS_FILE, [])


def save_order(order_data: dict):
    orders = load_orders()
    orders.append(order_data)
    save_json(ORDERS_FILE, orders)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS if ADMIN_USER_IDS else True


def get_font(size: int):
    if FONT_PATH and Path(FONT_PATH).exists():
        return ImageFont.truetype(FONT_PATH, size=size)
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_banner(headline: str, subtext: str, cta: str, output_name: str = "banner") -> Path:
    width, height = 1280, 1280
    if BACKGROUND_PATH.exists():
        image = Image.open(BACKGROUND_PATH).convert("RGBA").resize((width, height))
    else:
        image = Image.new("RGBA", (width, height), (10, 26, 60, 255))
        overlay = Image.new("RGBA", (width, height), (20, 130, 220, 70))
        image = Image.alpha_composite(image, overlay)

    draw = ImageDraw.Draw(image)
    title_font = get_font(74)
    body_font = get_font(42)
    small_font = get_font(34)

    draw.rounded_rectangle((60, 60, width - 60, height - 60), radius=40, outline=(255, 255, 255, 80), width=3)

    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((220, 220))
        image.alpha_composite(logo, (90, 90))

    headline_lines = wrap_text(draw, headline, title_font, width - 180)
    y = 340
    for line in headline_lines:
        draw.text((90, y), line, font=title_font, fill=(255, 255, 255, 255))
        y += 92

    sub_lines = wrap_text(draw, subtext, body_font, width - 180)
    y += 20
    for line in sub_lines:
        draw.text((90, y), line, font=body_font, fill=(210, 235, 255, 255))
        y += 58

    draw.rounded_rectangle((90, height - 240, width - 90, height - 140), radius=24, fill=(255, 255, 255, 240))
    draw.text((130, height - 215), cta, font=small_font, fill=(15, 35, 70, 255))
    draw.text((90, height - 90), "SDM SMM PANEL  |  https://sdmpanel.co.in  |  t.me/sdmsmmpanel", font=get_font(28), fill=(255, 255, 255, 220))

    output_path = GENERATED_DIR / f"{output_name}_{int(datetime.utcnow().timestamp())}.png"
    image.convert("RGB").save(output_path, quality=95)
    return output_path


def choose_best_post_time(now: datetime) -> datetime:
    preferred_hours = [9, 12, 15, 18, 21]
    candidates = []
    for hour in preferred_hours:
        candidate = now.replace(hour=hour, minute=random.randint(0, 20), second=0, microsecond=0)
        if candidate > now:
            candidates.append(candidate)
    if candidates:
        return candidates[0]
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=9, minute=random.randint(0, 20), second=0, microsecond=0)


def format_deal_post(deal: dict) -> str:
    return (
        f"💰 {deal['title']}\n\n"
        f"{deal['details']}\n"
        f"{deal['price']}\n\n"
        f"🔥 Limited deal\n"
        f"🌐 {WEBSITE_URL}\n"
        f"📢 t.me/sdmsmmpanel\n\n"
        f"{deal['cta']}"
    )


def create_website_order(order_data: dict) -> dict:
    if not WEBSITE_ORDER_API:
        return {
            "status": "saved_locally",
            "message": "Order saved locally. Add WEBSITE_ORDER_API to push orders to your website.",
        }

    headers = {"Content-Type": "application/json"}
    if WEBSITE_API_KEY:
        headers["Authorization"] = f"Bearer {WEBSITE_API_KEY}"

    response = requests.post(
        WEBSITE_ORDER_API,
        json=order_data,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    try:
        return response.json()
    except Exception:
        return {"status": "submitted", "message": response.text[:300]}


async def send_channel_content(bot, text: str, image_path: Path | None = None):
    if image_path and image_path.exists():
        with open(image_path, "rb") as f:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=f, caption=text[:1024])
    else:
        await bot.send_message(chat_id=CHANNEL_ID, text=text)


async def autopost_loop(app: Application):
    await app.bot.initialize()
    while True:
        now = datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)
        next_run = choose_best_post_time(now)
        delay = max(60, int((next_run - now).total_seconds()))
        logger.info("Next scheduled post at %s", next_run.isoformat())
        await asyncio.sleep(delay)

        try:
            post_type = random.choice(["promo", "promo", "deal", "banner"])
            posts = load_posts()
            deals = load_deals()

            if post_type == "deal" and deals:
                deal = random.choice(deals)
                text = format_deal_post(deal)
                banner = generate_banner(deal["title"], deal["details"], deal["price"], "deal")
                await send_channel_content(app.bot, text, banner)

            elif post_type == "banner" and posts:
                post = random.choice(posts)
                lines = post["text"].split("\n")
                headline = lines[0][:60]
                subtext = " ".join(line for line in lines[1:4] if line.strip())[:120]
                banner = generate_banner(headline, subtext or "Fast • Cheap • Reliable", "Order now at sdmpanel.co.in", "promo")
                await send_channel_content(app.bot, post["text"], banner)

            elif posts:
                post = random.choice(posts)
                await send_channel_content(app.bot, post["text"])

            pause_minutes = random.randint(MIN_POST_GAP_MINUTES, MAX_POST_GAP_MINUTES)
            logger.info("Cooldown after post: %s minutes", pause_minutes)
            await asyncio.sleep(pause_minutes * 60)

        except Exception as exc:
            logger.exception("Autopost failed: %s", exc)
            await asyncio.sleep(300)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 SDM SMM Panel Bot Active\n\n"
        "Commands:\n"
        "/post your custom message\n"
        "/deal Title | Price | Details\n"
        "/banner Headline | Subtext | CTA\n"
        "/order name | service | qty | link\n"
        "/addreply keyword | reply text\n"
        "/help"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Not allowed.")
        return
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /post your message")
        return
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    await update.message.reply_text("✅ Custom post published to channel")


async def deal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Not allowed.")
        return
    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 3:
        await update.message.reply_text("Usage: /deal Title | Price | Details")
        return
    deal = {
        "title": parts[0],
        "price": parts[1],
        "details": parts[2],
        "cta": f"Order now at {WEBSITE_URL}",
    }
    deals = load_deals()
    deals.append(deal)
    save_json(DEALS_FILE, deals)
    text = format_deal_post(deal)
    banner = generate_banner(deal["title"], deal["details"], deal["price"], "manual_deal")
    await send_channel_content(context.bot, text, banner)
    await update.message.reply_text("✅ Deal added and posted")


async def banner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Not allowed.")
        return
    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 3:
        await update.message.reply_text("Usage: /banner Headline | Subtext | CTA")
        return
    path = generate_banner(parts[0], parts[1], parts[2], "custom")
    caption = f"{parts[0]}\n\n{parts[1]}\n\n🌐 {WEBSITE_URL}\n📢 t.me/sdmsmmpanel"
    await send_channel_content(context.bot, caption, path)
    await update.message.reply_text("✅ Banner generated and posted")


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 4:
        await update.message.reply_text("Usage: /order name | service | qty | link")
        return

    order_data = {
        "name": parts[0],
        "service": parts[1],
        "quantity": parts[2],
        "target_link": parts[3],
        "telegram_user_id": update.effective_user.id,
        "telegram_username": update.effective_user.username or "",
        "created_at": datetime.utcnow().isoformat(),
        "source": "telegram_bot",
    }

    save_order(order_data)

    try:
        website_result = create_website_order(order_data)
        await update.message.reply_text(
            "✅ Order request received.\n"
            f"Status: {website_result.get('status', 'submitted')}\n"
            f"Message: {website_result.get('message', 'Processed')}"
        )
    except Exception:
        await update.message.reply_text(
            "✅ Order saved by bot, but website API is not connected yet.\n"
            f"Complete manually on {WEBSITE_URL} or add WEBSITE_ORDER_API in Railway."
        )


async def addreply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Not allowed.")
        return
    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|", 1)]
    if len(parts) != 2:
        await update.message.reply_text("Usage: /addreply keyword | reply text")
        return
    AUTO_REPLIES[parts[0].lower()] = parts[1]
    await update.message.reply_text("✅ Auto reply added for keyword")


async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    text = update.message.text.lower()
    for keyword, reply in AUTO_REPLIES.items():
        if keyword in text:
            await update.message.reply_text(reply)
            return


async def private_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        "Hi 👋 Use /help to see commands.\n"
        f"You can also order directly from {WEBSITE_URL}"
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")

    ensure_dirs()
    ensure_json(POSTS_FILE, DEFAULT_POSTS)
    ensure_json(DEALS_FILE, DEFAULT_DEALS)
    ensure_json(ORDERS_FILE, [])

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("deal", deal_command))
    app.add_handler(CommandHandler("banner", banner_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("addreply", addreply_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, private_fallback))

    loop = asyncio.get_event_loop()
    loop.create_task(autopost_loop(app))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
