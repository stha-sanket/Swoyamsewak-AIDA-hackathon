from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace this with your bot's API key
API_KEY = '8200120783:AAEs9qK64Y6Cl8_Tj1h6ZeoB_2h8x1ON0dU'

# This function will handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your bot. Send me a message.')

# This function will handle text messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

def main():
    # Create the Application
    app = Application.builder().token(API_KEY).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()