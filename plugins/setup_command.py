#(©)CodeXBotz
# Add this file to your plugins folder: plugins/setup_command.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import OWNER_ID
from database.database import settings_collection
import asyncio

# Helper function to get setting
async def get_setting(key, default=None):
    setting = settings_collection.find_one({'_id': key})
    if setting:
        return setting.get('value', default)
    return default

# Helper function to update setting
async def update_setting(key, value):
    settings_collection.update_one(
        {'_id': key},
        {'$set': {'value': value}},
        upsert=True
    )

@Bot.on_message(filters.private & filters.user(OWNER_ID) & filters.command('setup'))
async def setup_command(client: Bot, message: Message):
    setup_text = """
🔧 <b>Bot Configuration Setup</b>

Choose what you want to configure:

1️⃣ <b>Start Message</b> - Customize welcome message
2️⃣ <b>Force Sub Message</b> - Customize force subscribe message
3️⃣ <b>Force Sub Channel</b> - Set force subscribe channel
4️⃣ <b>Start Picture</b> - Set start message image
5️⃣ <b>Custom Caption</b> - Set custom file caption
6️⃣ <b>Protect Content</b> - Enable/disable forward protection
7️⃣ <b>Auto Delete Time</b> - Set auto-delete duration
8️⃣ <b>Auto Delete Messages</b> - Customize deletion messages
9️⃣ <b>Channel Button</b> - Enable/disable share button
🔟 <b>User Reply Text</b> - Auto-reply to user messages
1️⃣1️⃣ <b>Bot Stats Text</b> - Customize stats message
1️⃣2️⃣ <b>Join Request</b> - Enable/disable join request
1️⃣3️⃣ <b>View Current Settings</b> - See all settings

<b>Usage:</b>
<code>/setup start_msg</code> - Configure start message
<code>/setup force_msg</code> - Configure force sub message
<code>/setup force_channel</code> - Set force sub channel ID
<code>/setup start_pic</code> - Set start picture URL
<code>/setup caption</code> - Set custom caption
<code>/setup protect</code> - Toggle content protection
<code>/setup autodel</code> - Set auto-delete time
<code>/setup autodel_msg</code> - Set auto-delete message
<code>/setup autodel_success</code> - Set success message
<code>/setup channel_btn</code> - Toggle channel button
<code>/setup user_reply</code> - Set user reply text
<code>/setup stats_text</code> - Set stats text
<code>/setup join_request</code> - Toggle join request
<code>/setup view</code> - View all settings
<code>/setup reset</code> - Reset to defaults
"""
    
    await message.reply_text(setup_text, quote=True)

@Bot.on_message(filters.private & filters.user(OWNER_ID) & filters.command('setup') & filters.regex(r'^/setup\s+\w+'))
async def setup_options(client: Bot, message: Message):
    try:
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            return
        
        option = command_parts[1].lower()
        
        if option == 'view':
            await show_current_settings(client, message)
        elif option == 'reset':
            await reset_settings(client, message)
        elif option == 'start_msg':
            await setup_start_message(client, message)
        elif option == 'force_msg':
            await setup_force_message(client, message)
        elif option == 'force_channel':
            await setup_force_channel(client, message)
        elif option == 'start_pic':
            await setup_start_pic(client, message)
        elif option == 'caption':
            await setup_caption(client, message)
        elif option == 'protect':
            await setup_protect_content(client, message)
        elif option == 'autodel':
            await setup_auto_delete(client, message)
        elif option == 'autodel_msg':
            await setup_auto_delete_msg(client, message)
        elif option == 'autodel_success':
            await setup_auto_delete_success(client, message)
        elif option == 'channel_btn':
            await setup_channel_button(client, message)
        elif option == 'user_reply':
            await setup_user_reply(client, message)
        elif option == 'stats_text':
            await setup_stats_text(client, message)
        elif option == 'join_request':
            await setup_join_request(client, message)
        else:
            await message.reply_text("❌ Invalid option! Use <code>/setup</code> to see all options.", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}", quote=True)

async def show_current_settings(client: Bot, message: Message):
    settings_text = """
📋 <b>Current Bot Settings</b>

<b>Start Message:</b>
<code>{start_msg}</code>

<b>Force Sub Message:</b>
<code>{force_msg}</code>

<b>Force Sub Channel:</b> <code>{force_channel}</code>

<b>Start Picture:</b> <code>{start_pic}</code>

<b>Custom Caption:</b> <code>{caption}</code>

<b>Protect Content:</b> <code>{protect}</code>

<b>Auto Delete Time:</b> <code>{autodel} seconds</code>

<b>Auto Delete Message:</b>
<code>{autodel_msg}</code>

<b>Auto Delete Success:</b>
<code>{autodel_success}</code>

<b>Disable Channel Button:</b> <code>{channel_btn}</code>

<b>User Reply Text:</b>
<code>{user_reply}</code>

<b>Bot Stats Text:</b>
<code>{stats_text}</code>

<b>Join Request Enabled:</b> <code>{join_request}</code>
"""
    
    start_msg = await get_setting('start_msg', 'Not Set')
    force_msg = await get_setting('force_msg', 'Not Set')
    force_channel = await get_setting('force_channel', '0')
    start_pic = await get_setting('start_pic', 'Not Set')
    caption = await get_setting('caption', 'Not Set')
    protect = await get_setting('protect_content', 'False')
    autodel = await get_setting('auto_delete_time', '0')
    autodel_msg = await get_setting('auto_delete_msg', 'Not Set')
    autodel_success = await get_setting('auto_delete_success', 'Not Set')
    channel_btn = await get_setting('disable_channel_button', 'False')
    user_reply = await get_setting('user_reply', 'Not Set')
    stats_text = await get_setting('stats_text', 'Not Set')
    join_request = await get_setting('join_request', 'False')
    
    formatted_text = settings_text.format(
        start_msg=start_msg[:100] + '...' if len(str(start_msg)) > 100 else start_msg,
        force_msg=force_msg[:100] + '...' if len(str(force_msg)) > 100 else force_msg,
        force_channel=force_channel,
        start_pic=start_pic[:50] + '...' if len(str(start_pic)) > 50 else start_pic,
        caption=caption[:50] + '...' if len(str(caption)) > 50 else caption,
        protect=protect,
        autodel=autodel,
        autodel_msg=autodel_msg[:100] + '...' if len(str(autodel_msg)) > 100 else autodel_msg,
        autodel_success=autodel_success[:100] + '...' if len(str(autodel_success)) > 100 else autodel_success,
        channel_btn=channel_btn,
        user_reply=user_reply[:100] + '...' if len(str(user_reply)) > 100 else user_reply,
        stats_text=stats_text[:100] + '...' if len(str(stats_text)) > 100 else stats_text,
        join_request=join_request
    )
    
    await message.reply_text(formatted_text, quote=True)

async def reset_settings(client: Bot, message: Message):
    confirm_msg = await message.reply_text(
        "⚠️ <b>Are you sure you want to reset all settings to default?</b>\n\n"
        "Reply with <code>YES</code> to confirm or <code>NO</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=30)
        if response.text.upper() == 'YES':
            # Clear all settings
            settings_collection.delete_many({})
            await response.reply_text("✅ All settings have been reset to default values!")
        else:
            await response.reply_text("❌ Reset cancelled.")
    except asyncio.TimeoutError:
        await confirm_msg.edit_text("⏱️ Timeout! Reset cancelled.")

async def setup_start_message(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup Start Message</b>\n\n"
        "Send me the start message you want to use.\n\n"
        "<b>Available placeholders:</b>\n"
        "<code>{first}</code> - User first name\n"
        "<code>{last}</code> - User last name\n"
        "<code>{username}</code> - Username\n"
        "<code>{mention}</code> - Mention user\n"
        "<code>{id}</code> - User ID\n\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        await update_setting('start_msg', response.text)
        await response.reply_text(
            f"✅ <b>Start message updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            quote=True
        )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_force_message(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup Force Subscribe Message</b>\n\n"
        "Send me the force subscribe message.\n\n"
        "<b>Available placeholders:</b>\n"
        "<code>{first}</code> - User first name\n"
        "<code>{last}</code> - User last name\n"
        "<code>{username}</code> - Username\n"
        "<code>{mention}</code> - Mention user\n"
        "<code>{id}</code> - User ID\n\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        await update_setting('force_msg', response.text)
        await response.reply_text(
            f"✅ <b>Force subscribe message updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            quote=True
        )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_force_channel(client: Bot, message: Message):
    await message.reply_text(
        "🔢 <b>Setup Force Subscribe Channel</b>\n\n"
        "Send me the channel ID (e.g., <code>-1001234567890</code>)\n"
        "Send <code>0</code> to disable force subscribe\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=60)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        try:
            channel_id = int(response.text)
            if channel_id != 0:
                # Verify the channel
                try:
                    chat = await client.get_chat(channel_id)
                    await update_setting('force_channel', str(channel_id))
                    await response.reply_text(
                        f"✅ <b>Force subscribe channel updated!</b>\n\n"
                        f"<b>Channel:</b> {chat.title}\n"
                        f"<b>ID:</b> <code>{channel_id}</code>",
                        quote=True
                    )
                except Exception as e:
                    await response.reply_text(
                        f"❌ <b>Error:</b> Could not access channel.\n"
                        f"Make sure bot is admin in the channel!\n\n"
                        f"Error: {str(e)}",
                        quote=True
                    )
            else:
                await update_setting('force_channel', '0')
                await response.reply_text("✅ Force subscribe disabled!", quote=True)
        except ValueError:
            await response.reply_text("❌ Invalid channel ID! Please send a valid number.", quote=True)
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_start_pic(client: Bot, message: Message):
    await message.reply_text(
        "🖼️ <b>Setup Start Picture</b>\n\n"
        "Send me the image URL or send <code>none</code> to remove.\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=60)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        if response.text.lower() == 'none':
            await update_setting('start_pic', '')
            await response.reply_text("✅ Start picture removed!", quote=True)
        else:
            await update_setting('start_pic', response.text)
            await response.reply_text(
                f"✅ <b>Start picture updated!</b>\n\n<b>URL:</b> <code>{response.text}</code>",
                quote=True
            )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_caption(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup Custom Caption</b>\n\n"
        "Send me the custom caption for files.\n\n"
        "<b>Available placeholders:</b>\n"
        "<code>{filename}</code> - File name\n"
        "<code>{previouscaption}</code> - Original caption\n\n"
        "Send <code>none</code> to disable custom caption.\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        if response.text.lower() == 'none':
            await update_setting('caption', '')
            await response.reply_text("✅ Custom caption disabled!", quote=True)
        else:
            await update_setting('caption', response.text)
            await response.reply_text(
                f"✅ <b>Custom caption updated!</b>\n\n<b>Preview:</b>\n{response.text}",
                quote=True
            )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_protect_content(client: Bot, message: Message):
    current = await get_setting('protect_content', 'False')
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Enable", callback_data="protect_true"),
            InlineKeyboardButton("❌ Disable", callback_data="protect_false")
        ]
    ])
    
    await message.reply_text(
        f"🔒 <b>Protect Content</b>\n\n"
        f"<b>Current Status:</b> <code>{current}</code>\n\n"
        f"Enable to prevent users from forwarding files.",
        reply_markup=buttons,
        quote=True
    )

async def setup_auto_delete(client: Bot, message: Message):
    await message.reply_text(
        "⏱️ <b>Setup Auto Delete Time</b>\n\n"
        "Send me the time in seconds for auto-deletion.\n"
        "Send <code>0</code> to disable auto-delete.\n\n"
        "<b>Examples:</b>\n"
        "<code>300</code> - 5 minutes\n"
        "<code>600</code> - 10 minutes\n"
        "<code>1800</code> - 30 minutes\n\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=60)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        try:
            seconds = int(response.text)
            if seconds < 0:
                await response.reply_text("❌ Please send a positive number!", quote=True)
                return
            
            await update_setting('auto_delete_time', str(seconds))
            
            if seconds == 0:
                await response.reply_text("✅ Auto-delete disabled!", quote=True)
            else:
                mins = seconds // 60
                await response.reply_text(
                    f"✅ <b>Auto-delete time updated!</b>\n\n"
                    f"<b>Time:</b> {seconds} seconds ({mins} minutes)",
                    quote=True
                )
        except ValueError:
            await response.reply_text("❌ Invalid number! Please send a valid number.", quote=True)
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_auto_delete_msg(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup Auto Delete Message</b>\n\n"
        "Send me the message to show before auto-deletion.\n\n"
        "<b>Available placeholder:</b>\n"
        "<code>{time}</code> - Time in seconds\n\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        await update_setting('auto_delete_msg', response.text)
        await response.reply_text(
            f"✅ <b>Auto-delete message updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            quote=True
        )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_auto_delete_success(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup Auto Delete Success Message</b>\n\n"
        "Send me the message to show after deletion.\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        await update_setting('auto_delete_success', response.text)
        await response.reply_text(
            f"✅ <b>Success message updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            quote=True
        )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_channel_button(client: Bot, message: Message):
    current = await get_setting('disable_channel_button', 'False')
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Enable Button", callback_data="channel_btn_false"),
            InlineKeyboardButton("❌ Disable Button", callback_data="channel_btn_true")
        ]
    ])
    
    await message.reply_text(
        f"🔘 <b>Channel Share Button</b>\n\n"
        f"<b>Current Status:</b> <code>{'Disabled' if current == 'True' else 'Enabled'}</code>\n\n"
        f"Choose whether to show share button on channel posts.",
        reply_markup=buttons,
        quote=True
    )

async def setup_user_reply(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup User Reply Text</b>\n\n"
        "Send me the auto-reply message for user DMs.\n"
        "Send <code>none</code> to disable auto-reply.\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        if response.text.lower() == 'none':
            await update_setting('user_reply', '')
            await response.reply_text("✅ User auto-reply disabled!", quote=True)
        else:
            await update_setting('user_reply', response.text)
            await response.reply_text(
                f"✅ <b>User reply text updated!</b>\n\n<b>Preview:</b>\n{response.text}",
                quote=True
            )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_stats_text(client: Bot, message: Message):
    await message.reply_text(
        "📝 <b>Setup Bot Stats Text</b>\n\n"
        "Send me the stats message format.\n\n"
        "<b>Available placeholder:</b>\n"
        "<code>{uptime}</code> - Bot uptime\n\n"
        "Send <code>cancel</code> to cancel.",
        quote=True
    )
    
    try:
        response = await client.listen(message.chat.id, timeout=120)
        if response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        await update_setting('stats_text', response.text)
        await response.reply_text(
            f"✅ <b>Stats text updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            quote=True
        )
    except asyncio.TimeoutError:
        await message.reply_text("⏱️ Timeout! Operation cancelled.")

async def setup_join_request(client: Bot, message: Message):
    current = await get_setting('join_request', 'False')
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Enable", callback_data="join_req_true"),
            InlineKeyboardButton("❌ Disable", callback_data="join_req_false")
        ]
    ])
    
    await message.reply_text(
        f"📝 <b>Join Request Feature</b>\n\n"
        f"<b>Current Status:</b> <code>{current}</code>\n\n"
        f"Enable to use join request instead of direct channel join.",
        reply_markup=buttons,
        quote=True
    )

# Callback query handlers
@Bot.on_callback_query(filters.regex(r'^protect_'))
async def protect_callback(client: Bot, query):
    if query.from_user.id != OWNER_ID:
        await query.answer("❌ Only owner can use this!", show_alert=True)
        return
    
    value = query.data.split('_')[1]
    await update_setting('protect_content', value.capitalize())
    await query.answer(f"✅ Content protection {'enabled' if value == 'true' else 'disabled'}!", show_alert=True)
    await query.message.edit_text(
        f"✅ <b>Content Protection Updated!</b>\n\n"
        f"<b>Status:</b> <code>{'Enabled' if value == 'true' else 'Disabled'}</code>"
    )

@Bot.on_callback_query(filters.regex(r'^channel_btn_'))
async def channel_btn_callback(client: Bot, query):
    if query.from_user.id != OWNER_ID:
        await query.answer("❌ Only owner can use this!", show_alert=True)
        return
    
    value = query.data.split('_')[-1]
    await update_setting('disable_channel_button', value.capitalize())
    await query.answer(f"✅ Channel button {'disabled' if value == 'true' else 'enabled'}!", show_alert=True)
    await query.message.edit_text(
        f"✅ <b>Channel Button Updated!</b>\n\n"
        f"<b>Status:</b> <code>{'Disabled' if value == 'true' else 'Enabled'}</code>"
    )

@Bot.on_callback_query(filters.regex(r'^join_req_'))
async def join_req_callback(client: Bot, query):
    if query.from_user.id != OWNER_ID:
        await query.answer("❌ Only owner can use this!", show_alert=True)
        return
    
    value = query.data.split('_')[-1]
    await update_setting('join_request', value.capitalize())
    await query.answer(f"✅ Join request {'enabled' if value == 'true' else 'disabled'}!", show_alert=True)
    await query.message.edit_text(
        f"✅ <b>Join Request Updated!</b>\n\n"
        f"<b>Status:</b> <code>{'Enabled' if value == 'true' else 'Disabled'}</code>"
    )