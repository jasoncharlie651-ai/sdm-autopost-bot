import asyncio
import random
import os

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


posts = [

"🚀 Skyrocket your social media success!\nGet real followers, likes & views in minutes.\n🌐 https://sdmpanel.co.in\n📢 https://t.me/sdmsmmpanel?direct",

"💥 Want viral growth?\nInstant followers, likes & watchtime.\n🌐 https://sdmpanel.co.in\n📢 https://t.me/sdmsmmpanel?direct",

"📊 Boost your brand presence now!\nAuthentic SMM services.\n🌐 https://sdmpanel.co.in\n📢 https://t.me/sdmsmmpanel?direct",

"🌟 Be the next trending creator!\nQuality engagement services.\n🌐 https://sdmpanel.co.in",

"🔥 Supercharge your social proof!\nReal results fast.\n🌐 https://sdmpanel.co.in",

"⚡ Instant boost for influencers!\nTikTok • Instagram • YouTube\n🌐 https://sdmpanel.co.in"

]


AUTO_REPLIES = {

"price": f"💰 Check services:\n{WEBSITE}",

"panel": f"🚀 Order here:\n{WEBSITE}",

"followers": f"📈 Boost followers instantly:\n{WEBSITE}",

"buy": f"🛒 Order now:\n{WEBSITE}"

}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 SDM SMM PANEL BOT

Commands:

/generate  - random promo text
/reseller  - get referral link
"""

    await update.message.reply_text(text)


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(random.choice(posts))


async def reseller(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    link = f"https://t.me/sdmsmmpanel?start=ref{user_id}"

    text = f"""
💼 RESELLER PROGRAM

Invite users and earn.

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

        text = random.choice(posts)

        await app.bot.send_message(

            chat_id=CHANNEL_ID,

            text=text

        )

        wait = random.randint(2,3) * 3600

        print(f"Next post in {wait/3600} hours")

        await asyncio.sleep(wait)


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("generate", generate))

    app.add_handler(CommandHandler("reseller", reseller))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, autoreply))

    asyncio.get_event_loop().create_task(autopost(app))

    app.run_polling()


if __name__ == "__main__":
    main()
