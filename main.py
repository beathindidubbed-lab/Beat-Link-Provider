import asyncio
from bot import Bot
from pyrogram import idle

async def main():
    app = Bot()
    await app.start()
    await idle()

asyncio.run(main())
