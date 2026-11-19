import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Set these in your environment before running:
# BOT_TOKEN="your-token-from-BotFather"
# ADMIN_ID="your-numeric-telegram-user-id"

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

WELCOME = (
    "مرحباً بك في FF RECOVERY BOT 🎮\n\n"
    "أساعدك في معرفة خطوات استرجاع حساب Free Fire عبر القنوات الرسمية.\n"
    "أرسل /help لمعرفة الأوامر.\n\n"
    "تنبيه: لا ترسل كلمة المرور أو رمز التحقق أو مفاتيح API لأي شخص."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/request - إرسال طلب مساعدة\n\n"
        "اكتب /request ثم اشرح المشكلة دون مشاركة كلمات المرور أو رموز التحقق."
    )

async def request_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_for_request"] = True
    await update.message.reply_text(
        "اكتب وصف المشكلة باختصار. لا ترسل كلمة المرور أو رمز التحقق أو معلومات الدفع."
    )

async def receive_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_request"):
        await update.message.reply_text("لإرسال طلب مساعدة، اكتب /request.")
        return

    context.user_data["waiting_for_request"] = False
    user = update.effective_user
    text = update.message.text or ""
    safe_text = text[:3000]

    await update.message.reply_text(
        "تم استلام طلبك. لا تشارك أي بيانات سرية؛ تابع تعليمات الاسترجاع الرسمية."
    )

    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=(
                    "طلب مساعدة جديد\n"
                    f"الاسم: {user.full_name}\n"
                    f"المعرّف: {user.id}\n"
                    f"اسم المستخدم: @{user.username or 'غير متوفر'}\n\n"
                    f"الوصف:\n{safe_text}"
                ),
            )
        except Exception:
            log.exception("Could not forward request to admin")

def main():
    if not TOKEN:
        raise RuntimeError("Set BOT_TOKEN environment variable first.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("request", request_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_request))
    app.run_polling()

if __name__ == "__main__":
    main()
