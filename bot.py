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

"🔥 Supercharge your social proof!\nReal results fast.\n🌐 https://sdmpanel.co.in",

"⚡ Instant boost for influencers!\nTikTok • Instagram • YouTube\n🌐 https://sdmpanel.co.in"
]

AUTO_REPLIES = {
"price": f"💰 Check services:\n{WEBSITE}",
"panel": f"🚀 Order here:\n{WEBSITE}",
"followers": f"📈 Boost followers instantly:\n{WEBSITE}",
"buy": f"🛒 Order now:\n{WEBSITE}"
}

def create_ai_banner(title, subtitle, color1, color2):

    width = 1200
    height = 1200

    # create gradient background
    img = Image.new("RGB", (width, height), color1)
    draw = ImageDraw.Draw(img)

    for i in range(height):
        r = int(color1[0] + (color2[0]-color1[0]) * i/height)
        g = int(color1[1] + (color2[1]-color1[1]) * i/height)
        b = int(color1[2] + (color2[2]-color1[2]) * i/height)
        draw.line([(0,i),(width,i)], fill=(r,g,b))

    font_big = ImageFont.load_default()
    font_mid = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # logo
    try:
        logo = Image.open("assets/logo.png").resize((180,180))

        if logo.mode == "RGBA":
            img.paste(logo,(60,60),logo)
        else:
            img.paste(logo,(60,60))
    except:
        pass

    # headline
    draw.text(
        (120,350),
        title,
        fill="white",
        font=font_big
    )

    # subtitle
    draw.text(
        (120,500),
        subtitle,
        fill="white",
        font=font_mid
    )

    # feature bullets
    features = [
        "✔ Real Followers",
        "✔ Instant Delivery",
        "✔ Cheap Prices",
        "✔ 24/7 Panel"
    ]

    y = 650

    for f in features:
        draw.text((120,y), f, fill="white", font=font_small)
        y += 70

    # CTA
    draw.rectangle(
        [(120,900),(650,980)],
        fill=(255,255,255)
    )

    draw.text(
        (140,920),
        "ORDER NOW →",
        fill="black",
        font=font_small
    )

    # footer
    draw.text(
        (120,1050),
        "sdmpanel.co.in | t.me/sdmsmmpanel",
        fill="white",
        font=font_small
    )

    if not os.path.exists("banners"):
        os.mkdir("banners")

    path = f"banners/banner_{random.randint(1,999999)}.png"

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

    await update.message.reply_text("Banner posted.")


async def promo(update, context):

    image = create_ai_banner(
        "BOOST YOUR SOCIAL MEDIA 🚀",
        "Followers • Likes • Views • Subscribers",
        (30,60,200),
        (140,40,200)
    )

    await context.bot.send_photo(
        CHANNEL_ID,
        photo=open(image,"rb"),
        caption="🚀 Boost your social media instantly\nhttps://sdmpanel.co.in"
    )

    await update.message.reply_text("AI promo banner posted.")

async def deal_banner(update, context):

    image = create_ai_banner(
        "🔥 FLASH DEAL",
        "1000 Followers Starting ₹49",
        (200,50,50),
        (255,120,40)
    )

    await context.bot.send_photo(
        CHANNEL_ID,
        photo=open(image,"rb"),
        caption="💰 Limited time offer\nhttps://sdmpanel.co.in"
    )

    await update.message.reply_text("Deal banner posted.")

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

    await update.message.reply_text("Review banner posted.")


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

    await update.message.reply_text("Reseller banner posted.")


async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    text = """
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

Your referral link:
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
