# plugins/start.py - COMPLETELY REWRITTEN - THIS WILL WORK!

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import (ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
                    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, 
                    AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, 
                    FORCE_SUB_CHANNEL, OWNER_ID)
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user

# ===========================
# MAIN START HANDLER
# ===========================

@Bot.on_message(filters.command('start') & filters.private)
async def start_handler(client: Client, message: Message):
    """
    Main /start command handler
    Handles EVERYTHING - welcome, files, force sub
    """
    
    # Add user to database
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass
    
    # Get command text
    text = message.text
    
    # Check if there's a parameter (file link)
    has_parameter = False
    file_parameter = None
    
    if ' ' in text:
        parts = text.split(' ', 1)
        if len(parts) == 2 and parts[1].strip():
            has_parameter = True
            file_parameter = parts[1].strip()
    
    print(f"📨 /start from user {user_id}")
    print(f"   Has parameter: {has_parameter}")
    if has_parameter:
        print(f"   Parameter: {file_parameter[:30]}...")
    
    # If no parameter, just show welcome
    if not has_parameter:
        print("   → Showing welcome message")
        await show_welcome(client, message)
        return
    
    # Has parameter - user wants a file
    print("   → Processing file request")
    
    # Check force subscribe
    if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL != 0:
        # Check if user is subscribed
        try:
            member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
            is_subscribed = member.status not in ["kicked", "left"]
        except:
            is_subscribed = False
        
        if not is_subscribed:
            print(f"   → User not subscribed, showing force sub")
            await show_force_sub(client, message, file_parameter)
            return
    
    # User is subscribed (or no force sub), send the file
    print("   → User authorized, sending file")
    await send_file(client, message, file_parameter)


# ===========================
# WELCOME MESSAGE
# ===========================

async def show_welcome(client: Client, message: Message):
    """Show welcome message"""
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😊 About", callback_data="about"),
            InlineKeyboardButton("📚 Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    welcome_text = START_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name if message.from_user.last_name else "",
        username=f"@{message.from_user.username}" if message.from_user.username else "None",
        mention=message.from_user.mention,
        id=message.from_user.id
    )
    
    if START_PIC:
        try:
            await message.reply_photo(
                photo=START_PIC,
                caption=welcome_text,
                reply_markup=reply_markup,
                quote=True
            )
            return
        except Exception as e:
            print(f"Error sending photo: {e}")
    
    # Send text if photo failed or no photo
    await message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        quote=True
    )


# ===========================
# FORCE SUBSCRIBE
# ===========================

async def show_force_sub(client: Client, message: Message, file_parameter: str):
    """Show force subscribe message"""
    
    # Get invite link
    if bool(JOIN_REQUEST_ENABLE):
        try:
            invite = await client.create_chat_invite_link(
                chat_id=FORCE_SUB_CHANNEL,
                creates_join_request=True
            )
            button_url = invite.invite_link
        except:
            button_url = client.invitelink if hasattr(client, 'invitelink') else None
    else:
        button_url = client.invitelink if hasattr(client, 'invitelink') else None
    
    if not button_url:
        # Fallback
        button_url = f"https://t.me/c/{str(FORCE_SUB_CHANNEL)[4:]}/"
    
    # Create buttons
    buttons = [
        [InlineKeyboardButton("Join Channel", url=button_url)]
    ]
    
    # Add try again button with the same file parameter
    try_again_link = f"https://t.me/{client.username}?start={file_parameter}"
    buttons.append([
        InlineKeyboardButton("🔄 Try Again", url=try_again_link)
    ])
    
    force_text = FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name if message.from_user.last_name else "",
        username=f"@{message.from_user.username}" if message.from_user.username else "None",
        mention=message.from_user.mention,
        id=message.from_user.id
    )
    
    await message.reply_text(
        text=force_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )


# ===========================
# SEND FILE
# ===========================

async def send_file(client: Client, message: Message, file_parameter: str):
    """Decode parameter and send file(s)"""
    
    # Check db_channel
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply_text(
            "❌ <b>Bot Error!</b>\n\n"
            "Database channel not configured.\n"
            "Please contact admin.",
            quote=True
        )
        return
    
    # Decode the parameter
    try:
        decoded = await decode(file_parameter)
        print(f"   ✅ Decoded: {decoded}")
    except Exception as e:
        print(f"   ❌ Decode error: {e}")
        await message.reply_text(
            "❌ <b>Invalid Link!</b>\n\n"
            "This link is corrupted or expired.\n"
            "Please get a new link from the sender.",
            quote=True
        )
        return
    
    # Parse the decoded string
    # Format: get-{id} or get-{start_id}-{end_id}
    parts = decoded.split('-')
    
    if len(parts) < 2 or parts[0] != 'get':
        print(f"   ❌ Invalid format: {decoded}")
        await message.reply_text(
            "❌ <b>Invalid Link Format!</b>\n\n"
            "This link is not properly formatted.",
            quote=True
        )
        return
    
    # Calculate message IDs
    try:
        channel_id = abs(client.db_channel.id)
        
        if len(parts) == 2:
            # Single file: get-{id}
            msg_id = int(int(parts[1]) / channel_id)
            message_ids = [msg_id]
            print(f"   📄 Single file: message {msg_id}")
        
        elif len(parts) == 3:
            # Batch: get-{start}-{end}
            start_id = int(int(parts[1]) / channel_id)
            end_id = int(int(parts[2]) / channel_id)
            
            if start_id <= end_id:
                message_ids = list(range(start_id, end_id + 1))
            else:
                # Reverse range
                message_ids = list(range(start_id, end_id - 1, -1))
            
            print(f"   📦 Batch: {len(message_ids)} messages ({start_id} to {end_id})")
        
        else:
            raise ValueError(f"Invalid parts count: {len(parts)}")
    
    except Exception as e:
        print(f"   ❌ Parse error: {e}")
        await message.reply_text(
            "❌ <b>Link Processing Error!</b>\n\n"
            f"Could not process this link.\n"
            f"Error: <code>{str(e)}</code>",
            quote=True
        )
        return
    
    # Fetch messages
    temp_msg = await message.reply_text(
        "⏳ <b>Please wait...</b>\n"
        f"<i>Fetching {len(message_ids)} file(s)</i>",
        quote=True
    )
    
    try:
        messages = await get_messages(client, message_ids)
        print(f"   ✅ Fetched {len(messages)} messages")
    except Exception as e:
        print(f"   ❌ Fetch error: {e}")
        await temp_msg.edit_text(
            "❌ <b>Error Fetching Files!</b>\n\n"
            "The files may have been deleted or link is invalid.\n"
            "Please contact the person who shared this link."
        )
        return
    
    await temp_msg.delete()
    
    # Send files
    sent_messages = []
    
    for idx, msg in enumerate(messages, 1):
        try:
            # Prepare caption
            if CUSTOM_CAPTION and msg.document:
                prev_caption = msg.caption.html if msg.caption else ""
                filename = msg.document.file_name
                caption = CUSTOM_CAPTION.format(
                    previouscaption=prev_caption,
                    filename=filename
                )
            else:
                caption = msg.caption.html if msg.caption else ""
            
            # Prepare reply markup
            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None
            
            # Send the file
            copied = await msg.copy(
                chat_id=message.from_user.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                protect_content=PROTECT_CONTENT
            )
            
            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                sent_messages.append(copied)
            
            print(f"   ✅ Sent file {idx}/{len(messages)}")
            
            # Small delay between files
            if len(messages) > 1:
                await asyncio.sleep(0.5)
        
        except FloodWait as e:
            print(f"   ⏳ FloodWait: {e.value}s")
            await asyncio.sleep(e.value)
            # Retry
            try:
                copied = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                    sent_messages.append(copied)
            except Exception as retry_error:
                print(f"   ❌ Retry failed: {retry_error}")
        
        except Exception as e:
            print(f"   ❌ Error sending file {idx}: {e}")
            continue
    
    # Auto-delete if enabled
    if sent_messages and AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
        original_link = f"https://t.me/{client.username}?start={file_parameter}"
        
        delete_notice = await message.reply_text(
            AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME),
            quote=True
        )
        
        # Schedule deletion
        asyncio.create_task(delete_file(sent_messages, client, delete_notice, original_link))
        print(f"   ⏱️ Auto-delete scheduled for {AUTO_DELETE_TIME}s")
    
    print(f"   ✅ Done! Sent {len(sent_messages)} files")


# ===========================
# ADMIN COMMANDS
# ===========================

@Bot.on_message(filters.command('users') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def get_users(client: Bot, message: Message):
    """Get total users count"""
    msg = await message.reply_text("⏳ <b>Counting users...</b>", quote=True)
    users = await full_userbase()
    await msg.edit(f"👥 <b>Total Users:</b> <code>{len(users)}</code>")


@Bot.on_message(filters.command('broadcast') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def broadcast(client: Bot, message: Message):
    """Broadcast message to all users"""
    
    if not message.reply_to_message:
        await message.reply_text(
            "❌ <b>Usage:</b>\n\n"
            "Reply to a message with <code>/broadcast</code> to send it to all users.",
            quote=True
        )
        return
    
    users = await full_userbase()
    broadcast_msg = message.reply_to_message
    
    status_msg = await message.reply_text(
        "📢 <b>Broadcasting...</b>\n\n"
        f"Total users: {len(users)}\n"
        "Please wait...",
        quote=True
    )
    
    successful = 0
    blocked = 0
    deleted = 0
    failed = 0
    
    for user_id in users:
        try:
            await broadcast_msg.copy(user_id)
            successful += 1
        except UserIsBlocked:
            await del_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(user_id)
            deleted += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(user_id)
                successful += 1
            except:
                failed += 1
        except:
            failed += 1
    
    await status_msg.edit(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"📊 <b>Statistics:</b>\n"
        f"• Total: <code>{len(users)}</code>\n"
        f"• Successful: <code>{successful}</code>\n"
        f"• Blocked: <code>{blocked}</code>\n"
        f"• Deleted: <code>{deleted}</code>\n"
        f"• Failed: <code>{failed}</code>"
    )
