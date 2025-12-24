from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
import config
from datetime import datetime
from helper_func import get_readable_time

@Bot.on_message(filters.command('stats') & filters.user(config.ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    BOT_STATS_TEXT = config.get_bot_stats_text()
    await message.reply(BOT_STATS_TEXT.format(uptime=time))

@Bot.on_message(filters.private & filters.incoming)
async def useless(_,message: Message):
    USER_REPLY_TEXT = config.get_user_reply_text()
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)