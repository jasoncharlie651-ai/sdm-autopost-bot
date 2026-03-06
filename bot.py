import asyncio
import random
import os
from PIL import Image, ImageDraw, ImageFont

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

"🔥 Supercharge your social proof!\nReal results fast.\n🌐 https://sdmpanel.co.in\n📢 https://t.me/sdmsmmpanel?direct",

"⚡ Instant boost for influencers!\nTikTok • Instagram • YouTube\n🌐 https://sdmpanel.co.in",

"📈 More followers. More growth.\nTake your social media higher.\n🌐 https://sdmpanel.co.in",

"💎 The ultimate SMM solution!\nFor agencies & creators.\n🌐 https://sdmpanel.co.in",

"🚀 Level up your online game.\nTrusted SMM source.\n🌐 https://sdmpanel.co.in",

"🔝 Maximize your reach today!\nTikTok • Instagram • YouTube\n🌐 https://sdmpanel.co.in"
]

AUTO_REPLIES = {
"price": f"💰 Check latest services:\n{WEBSITE}",
"panel": f"🚀 Order here:\n{WEBSITE}",
"followers": f"📈 Boost followers instantly:\n{WEBSITE}",
"buy": f"🛒 Order now:\n{WEBSITE}"
}

def get_font(size):
    try:
        return ImageFont.truetype("assets/font.ttf", size)
    except:
        return ImageFont.load_default()

def create_banner(title, subtitle, color):

    width = 1200
    height = 1200

    img = Image.new("RGB",(width,height),color)

    draw = ImageDraw.Draw(img)

    font_big = get_font(70)
    font_small = get_font(40)

    logo = Image.open("assets/logo.png").resize((200,200))

    img.paste(logo,(50,50),logo)

    draw.text((120,400),title,fill="white",font=font_big)
    draw.text((120,600),subtitle,fill="white",font=font_small)

    draw.text(
    (120,1000),
    "sdmpanel.co.in | t.me/sdmsmmpanel",
    fill="white",
    font=font_small
    )

    if not os.path.exists("banners"):
        os.mkdir("banners")

    path = f"banners/banner_{random.randint(1,99999)}.png"

    img.save(path)

    return path

async def banner(update:Update,context:ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("Usage: /banner your text")
        return

    image = create_banner(text,"Followers • Likes • Views",(30,50,120))

    await context.bot.send_photo(
    chat_id=CHANNEL_ID,
    photo=open(image,"rb"),
    caption=text
    )

async def promo(update,context):

    image = create_banner(
    "BOOST YOUR SOCIAL MEDIA 🚀",
    "Followers • Likes • Views",
    (25,45,100)
    )

    await context.bot.send_photo(
    CHANNEL_ID,
    photo=open(image,"rb"),
    caption=f"🚀 Boost your social media instantly\n{WEBSITE}"
    )

async def deal_banner(update,context):

    image = create_banner(
    "🔥 FLASH DEAL",
    "1000 Followers Starting ₹49",
    (160,40,40)
    )

    await context.bot.send_photo(
    CHANNEL_ID,
    photo=open(image,"rb"),
    caption=f"💰 Limited offer\n{WEBSITE}"
    )

async def review_banner(update,context):

    image = create_banner(
    "⭐ CUSTOMER REVIEW",
    "Amazing SMM services!",
    (40,130,80)
    )

    await context.bot.send_photo(
    CHANNEL_ID,
    photo=open(image,"rb"),
    caption="⭐ Trusted worldwide"
    )

async def reseller_banner(update,context):

    image = create_banner(
    "💼 RESELLER PROGRAM",
    "Earn selling SMM services",
    (120,40,140)
    )

    await context.bot.send_photo(
    CHANNEL_ID,
    photo=open(image,"rb"),
    caption=f"Join reseller program\n{WEBSITE}"
    )

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    text = f"""
🤖 SDM SMM PANEL BOT

Commands:

/promo
/dealbanner
/reviewbanner
/resellerbanner
/banner text
/generate
/reseller
"""

    await update.message.reply_text(text)

async def generate(update,context):

    await update.message.reply_text(random.choice(posts))

async def reseller(update,context):

    user_id = update.effective_user.id

    link = f"https://t.me/sdmsmmpanel?start=ref{user_id}"

    text = f"""
💼 RESELLER PROGRAM

Invite users and earn.

Your link:
{link}

🌐 {WEBSITE}
"""

    await update.message.reply_text(text)

async def autoreply(update,context):

    text = update.message.text.lower()

    for key in AUTO_REPLIES:

        if key in text:

            await update.message.reply_text(AUTO_REPLIES[key])

            return

async def autopost(app):

    await app.bot.initialize()

    while True:

        text = random.choice(posts)

        image = create_banner(text,"",(25,45,100))

        await app.bot.send_photo(
        CHANNEL_ID,
        photo=open(image,"rb"),
        caption=text
        )

        wait = random.randint(2,3)*3600

        await asyncio.sleep(wait)

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("promo",promo))
    app.add_handler(CommandHandler("dealbanner",deal_banner))
    app.add_handler(CommandHandler("reviewbanner",review_banner))
    app.add_handler(CommandHandler("resellerbanner",reseller_banner))
    app.add_handler(CommandHandler("banner",banner))
    app.add_handler(CommandHandler("generate",generate))
    app.add_handler(CommandHandler("reseller",reseller))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,autoreply))

    loop = asyncio.get_event_loop()
    loop.create_task(autopost(app))

    app.run_polling()

if __name__ == "__main__":
    main()
