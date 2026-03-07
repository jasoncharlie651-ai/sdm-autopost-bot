import asyncio
import random
import os
import json

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_ID = "@sdmsmmpanel"

WEBSITE = "https://sdmpanel.co.in"
DIRECT = "https://t.me/sdmsmmpanel?direct"


# Load posts
with open("posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

# Load hashtag sets
with open("hashtags.json", "r", encoding="utf-8") as f:
    hashtags = json.load(f)


AUTO_REPLIES = {

"price": f"💰 Check our services:\n{WEBSITE}",

"panel": f"🚀 Order SMM services here:\n{WEBSITE}",

"followers": f"📈 Boost followers instantly:\n{WEBSITE}",

"buy": f"🛒 Start your order here:\n{WEBSITE}",

"smm": f"🌐 Visit our SMM Panel:\n{WEBSITE}"

}


def generate_message():

    post = random.choice(posts)["text"]

    tag = random.choice(hashtags)

    message = f"""{post}

🌐 {WEBSITE}
📢 {DIRECT}

{tag}
"""

    return message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 SDM SMM PANEL BOT

Commands:

/generate - generate promo message
/reseller - get referral link

Bot features:
• Auto marketing posts
• Anti-spam rotating hashtags
• Viral promo messages
"""

    await update.message.reply_text(text)


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = generate_message()

    await update.message.reply_text(message)


async def reseller(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    link = f"https://t.me/sdmsmmpanel?start=ref{user_id}"

    text = f"""
💼 RESELLER PROGRAM

Earn by inviting users.

Your referral link:
{link}

🌐 {WEBSITE}
"""

    await update.message.reply_text(text)


async def autoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    for key in AUTO_REPLIES:

        if key in text:

            await update.message.reply_text(AUTO_REPLIES[key])

            return


async def autopost(app):

    while True:

        message = generate_message()

        try:

            await app.bot.send_message(
                chat_id=CHANNEL_ID,
                text=message
            )

            print("Posted new promo message")

        except Exception as e:

            print("Posting error:", e)

        wait = random.randint(2, 3) * 3600

        print(f"Next post in {wait/3600} hours")

        await asyncio.sleep(wait)


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("generate", generate))

    app.add_handler(CommandHandler("reseller", reseller))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, autoreply))

    asyncio.get_event_loop().create_task(autopost(app))

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":

    main()
