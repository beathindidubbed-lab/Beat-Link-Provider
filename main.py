import asyncio
from bot import Bot
from pyrogram import idle

async def start_services():
    app = Bot()
    await app.start() # This starts the channel check in bot.py
    await idle()      # Keeps the bot listening for messages
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
