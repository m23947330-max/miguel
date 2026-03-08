import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token (muhit o‘zgaruvchisidan olinadi)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN muhit o‘zgaruvchisi o‘rnatilmagan!")

# Rasm fayli (loyiha ildizida bo‘lishi kerak)
IMAGE_FILE = "1.jpg"  # Rasm fayl nomi va kengaytmasi

# Render.com da avtomatik webhook URL yaratish
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    WEBHOOK_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}/webhook"
else:
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # fallback (agar localda sinab ko‘rmoqchi bo‘lsangiz)

# Render.com beradigan port
PORT = int(os.environ.get("PORT", 8443))

# Bir martalik parollar (kod ichida)
ONE_TIME_PASSWORDS = {
    'oxmygod': True,
    'megaladon': True,
    'ybanmikana': True,
    'oyboqmiya': True,
    'masayonmikan': True,
    'killone': True,
    'ajriq': True,
    'webgandon567': True,
    'itbet67': True,
    'eshakmiya123': True,
}

# Conversation state
AWAITING_PASSWORD = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum {user.first_name}! 👋\n\n"
        "Iltimos parolni kiriting:"
    )
    return AWAITING_PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_password = update.message.text.strip()
    
    if user_password in ONE_TIME_PASSWORDS:
        if ONE_TIME_PASSWORDS[user_password]:
            # Parolni ishlatilgan deb belgilash
            ONE_TIME_PASSWORDS[user_password] = False
            
            # Rasmni yuborish
            if os.path.exists(IMAGE_FILE):
                try:
                    with open(IMAGE_FILE, 'rb') as photo:
                        await update.message.reply_photo(
                            photo=photo,
                            caption="✅ Parol to'g'ri! Siz kirish huquqiga ega bo'ldingiz."
                        )
                except Exception as e:
                    logger.error(f"Rasm yuborishda xatolik: {e}")
                    await update.message.reply_text("❌ Rasm yuborishda muammo yuz berdi.")
            else:
                logger.error(f"Rasm fayli topilmadi: {IMAGE_FILE}")
                await update.message.reply_text("❌ Rasm fayli topilmadi.")
            
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "❌ Bu parol allaqachon ishlatilgan. Iltimos boshqa parolni kiriting."
            )
            return AWAITING_PASSWORD
    else:
        await update.message.reply_text(
            "❌ Parol noto'g'ri. Iltimos qayta urinib ko'ring."
        )
        return AWAITING_PASSWORD

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Suhbat bekor qilindi.")
    return ConversationHandler.END

def main():
    # Bot ilovasini yaratish
    application = Application.builder().token(TOKEN).build()

    # Conversation handlerni qo'shish
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAITING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)

    # Webhook orqali ishga tushirish
    logger.info(f"Webhook ishga tushmoqda: port {PORT}, url {WEBHOOK_URL}")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":

    main()
