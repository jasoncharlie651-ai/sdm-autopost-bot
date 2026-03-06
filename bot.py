import asyncio
import json
import random
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@sdmsmmpanel"

WEBSITE = "https://sdmpanel.co.in"
DIRECT = "https://t.me/sdmsmmpanel?direct"

posts = [

"🚀 Skyrocket your social media success!\nGet real followers, likes & views in minutes with SDM SMM Panel.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"💥 Want viral growth?\nSDM SMM Panel delivers instant followers, likes & watchtime.\nFast - Safe - Trusted\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"📊 Boost your brand presence now!\n100% authentic SMM services crafted for creators and marketers.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"🌟 Be the next trending creator!\nPowered by SDM SMM Panel — boosting your reach with quality engagement.\n🌐 https://sdmpanel.co.in",

"🔥 Supercharge your social proof!\nReal results, real fast, real affordable.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"⚡ Instant boost for influencers!\nGrow faster on TikTok, Instagram & YouTube with SDM SMM Panel.\n🌐 https://sdmpanel.co.in",

"📈 More followers. More likes. More growth.\nTake your social media to new heights with SDM SMM Panel.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"💎 The ultimate SMM solution!\nDesigned for agencies, creators & brands that demand quality.\n🌐 https://sdmpanel.co.in",

"🚀 Level up your online game.\nSDM SMM Panel = trusted source for social growth.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"🔝 Maximize your reach today!\nTikTok - Instagram - YouTube - Facebook\nAll from one panel — SDM SMM Panel\n🌐 https://sdmpanel.co.in",

"⚙️ Automated SMM services 24/7!\nFast delivery, best support, unbeatable prices.\n🌐 https://sdmpanel.co.in",

"💬 Social growth made simple.\nJust a few clicks on SDM SMM Panel and watch your numbers rise.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"🌈 Boost engagement across all platforms!\nFollowers, likes, views — all in one place.\n🌐 https://sdmpanel.co.in",

"🎯 Grow faster, smarter, cheaper!\nSDM SMM Panel helps you dominate your niche.\n🌐 https://sdmpanel.co.in",

"💡 Get noticed instantly!\nSDM SMM Panel delivers high-quality social media growth 24/7.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"🎬 Creators love SDM!\nQuick boosts for your YouTube and TikTok journey.\n🌐 https://sdmpanel.co.in",

"🚨 Don’t wait to go viral!\nSDM SMM Panel puts your brand in front of millions.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct",

"💪 Reliable SMM power for resellers & influencers.\nJoin SDM SMM Panel and start earning or growing today!\n🌐 https://sdmpanel.co.in",

"🏆 Enhance your digital influence effortlessly.\nTrusted by thousands worldwide — SDM SMM Panel\n🌐 https://sdmpanel.co.in",

"⚡ Your shortcut to social media fame!\nJoin SDM SMM Panel — quick, affordable & effective SMM services.\n🌐 https://sdmpanel.co.in | 📢 https://t.me/sdmsmmpanel?direct"

]

AUTO_REPLIES = {
"price": f"💰 Check latest services here:\n{WEBSITE}",
"panel": f"🚀 Order from SDM Panel:\n{WEBSITE}",
"followers": f"📈 Boost followers instantly:\n{WEBSITE}",
"buy": f"🛒 Order here:\n{WEBSITE}"
}

async def autopost(app):
    await app.bot.initialize()

    while True:

        post = random.choice(posts)

        await app.bot.send_message(CHANNEL_ID, post)

        wait = random.randint(2,3) * 3600

        await asyncio.sleep(wait)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = f"""
🤖 SDM PANEL BOT

Commands:

/generate - create promo
/reseller - reseller link
/order name | service | qty | link
"""

    await update.message.reply_text(text)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    post = random.choice(posts)

    await update.message.reply_text(post)

async def reseller(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    link = f"https://t.me/sdmsmmpanel?start=ref{user_id}"

    text = f"""
💼 SDM PANEL RESELLER PROGRAM

Invite users and earn rewards.

Your referral link:

{link}

🌐 {WEBSITE}
"""

    await update.message.reply_text(text)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    await update.message.reply_text(
f"""
✅ Order request received

Send order manually on website:

{WEBSITE}

Details:
{text}
"""
)

from PIL import Image, ImageDraw, ImageFont
import random

backgrounds = [
    "assets/bg1.png",
    "assets/bg2.png",
    "assets/bg3.png"
]

def generate_ai_banner(title):

    width = 1200
    height = 1200

    bg = Image.open(random.choice(backgrounds)).resize((width,height))

    draw = ImageDraw.Draw(bg)

    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()

    logo = Image.open("assets/logo.png").resize((200,200))

    bg.paste(logo,(60,60),logo)

    draw.text(
        (120,450),
        title,
        fill="white",
        font=font_big
    )

    draw.text(
        (120,650),
        "Followers • Likes • Views",
        fill="white",
        font=font_small
    )

    draw.text(
        (120,1000),
        "sdmpanel.co.in | t.me/sdmsmmpanel",
        fill="white",
        font=font_small
    )

    path="banner.png"

    bg.save(path)

    return path

async def banner(update, context):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("Usage: /banner Your text")
        return

    image = generate_ai_banner(text)

    await context.bot.send_photo(
        chat_id="@sdmsmmpanel",
        photo=open(image,"rb"),
        caption=text
    )

async def autoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    for key in AUTO_REPLIES:

        if key in text:

            await update.message.reply_text(AUTO_REPLIES[key])

            return
            
def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("reseller", reseller))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("banner", banner))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, autoreply))

    loop = asyncio.get_event_loop()

    loop.create_task(autopost(app))

    app.run_polling()

if __name__ == "__main__":
    main()
