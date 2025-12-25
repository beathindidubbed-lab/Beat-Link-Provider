# plugins/channel_post.py - Fixed version with proper db_channel access

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import OWNER_ID, ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

@Bot.on_message(filters.private & filters.user([OWNER_ID] + ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats','setup','help','custom_batch','range_help']))
async def channel_post(client: Client, message: Message):
    """Handle private messages from admins to create shareable links"""
    
    # Check if db_channel exists
    if not hasattr(client, 'db_channel') or client.db_channel is None:
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>\n\n"
            "Please restart the bot or contact admin.",
            quote=True
        )
        return
    
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    
    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(f"Error copying to DB channel: {e}")
        await reply_text.edit_text("❌ Something went wrong! Make sure bot is admin in database channel.")
        return
    
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]
    ])

    await reply_text.edit(
        f"<b>Here is your link</b>\n\n{link}",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await post_message.edit_reply_markup(reply_markup)
        except Exception:
            pass


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    """Automatically add share button to channel posts"""
    
    if DISABLE_CHANNEL_BUTTON:
        return
    
    # Check if db_channel exists
    if not hasattr(client, 'db_channel') or client.db_channel is None:
        print("⚠️ Warning: db_channel not available in new_post handler")
        return

    try:
        converted_id = message.id * abs(client.db_channel.id)
        string = f"get-{converted_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]
        ])
        
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(f"Error in new_post: {e}")
        pass
