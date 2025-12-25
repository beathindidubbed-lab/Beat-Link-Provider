import asyncio
import os
from bot import Bot
from pyrogram import idle

async def start_services():
    # TEMPORARY: Clear session on startup
    session_files = ['Bot.session', 'Bot.session-journal']
    for file in session_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Deleted old session file: {file}")
    
    app = Bot()
    await app.start()
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
