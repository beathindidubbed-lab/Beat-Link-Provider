# plugins/setup_panel.py
# (©)CodeXBotz - Advanced Interactive Setup Panel with Command Support

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import OWNER_ID, ADMINS
from database.database import get_setting, update_setting
import asyncio
from typing import Optional

# ===========================
# MENU CONSTANTS
# ===========================

MAIN_MENU_TEXT = """
╔═══════════════════════════╗
║  🎛️ <b>BOT SETUP PANEL</b> 🎛️  ║
╚═══════════════════════════╝

<b>Welcome to the Advanced Configuration Panel!</b>

Choose a category to configure:

🎨 <b>Appearance</b> - Start messages & images
📢 <b>Force Subscribe</b> - Channel join settings
📝 <b>Captions & Replies</b> - Custom messages
🔒 <b>Protection</b> - Content security settings
⏱️ <b>Auto Delete</b> - Automatic file deletion
⚙️ <b>Advanced</b> - Other bot settings

<b>💡 Quick Commands:</b>
<code>/setup start_msg</code> - Edit start message
<code>/setup force_channel</code> - Set channel ID
<code>/setup view</code> - View all settings
<code>/setup help</code> - Show all commands

<b>Current Status:</b> ✅ All systems operational
"""

HELP_TEXT = """
📚 <b>SETUP COMMAND GUIDE</b>

<b>🎨 Appearance Commands:</b>
• <code>/setup start_msg</code> - Edit welcome message
• <code>/setup start_pic</code> - Edit welcome image
• <code>/setup stats_text</code> - Edit stats format

<b>📢 Force Subscribe Commands:</b>
• <code>/setup force_channel</code> - Set channel ID
• <code>/setup force_msg</code> - Edit force message
• <code>/setup join_request</code> - Toggle join mode

<b>📝 Caption Commands:</b>
• <code>/setup caption</code> - Set custom caption
• <code>/setup user_reply</code> - Set auto-reply

<b>🔒 Protection Commands:</b>
• <code>/setup protect</code> - Toggle content protection
• <code>/setup channel_btn</code> - Toggle share button

<b>⏱️ Auto Delete Commands:</b>
• <code>/setup autodel_time</code> - Set delete timer
• <code>/setup autodel_msg</code> - Set warning message
• <code>/setup autodel_success</code> - Set success message

<b>⚙️ Advanced Commands:</b>
• <code>/setup view</code> - View all settings
• <code>/setup backup</code> - Backup configuration
• <code>/setup restore</code> - Restore from backup
• <code>/setup reset</code> - Reset to defaults

<b>Usage Examples:</b>
<code>/setup</code> - Open interactive panel
<code>/setup start_msg</code> - Direct command
<code>/setup view all</code> - View settings
"""

APPEARANCE_MENU = """
🎨 <b>APPEARANCE SETTINGS</b>

Configure how your bot greets users:

• <b>Start Message</b> - Welcome text
• <b>Start Picture</b> - Welcome image URL
• <b>Bot Stats Text</b> - /stats command format

<i>Tip: Use placeholders like {first}, {username}, {mention}</i>
"""

FORCE_SUB_MENU = """
📢 <b>FORCE SUBSCRIBE SETTINGS</b>

Control channel subscription requirements:

• <b>Force Channel ID</b> - Required channel
• <b>Force Sub Message</b> - Subscribe prompt
• <b>Join Request Mode</b> - Enable/Disable

<i>Current Channel:</i> <code>{channel}</code>
<i>Join Request:</i> <code>{join_req}</code>
"""

CAPTIONS_MENU = """
📝 <b>CAPTIONS & REPLIES</b>

Customize bot responses:

• <b>Custom Caption</b> - File captions
• <b>User Reply Text</b> - DM auto-reply

<i>Use {filename} and {previouscaption} in captions</i>
"""

PROTECTION_MENU = """
🔒 <b>PROTECTION SETTINGS</b>

Secure your content:

• <b>Protect Content</b> - Prevent forwarding
• <b>Channel Button</b> - Show/hide share button

<i>Current Protection:</i> <code>{protect}</code>
<i>Channel Button:</i> <code>{button}</code>
"""

AUTO_DELETE_MENU = """
⏱️ <b>AUTO DELETE SETTINGS</b>

Configure automatic file deletion:

• <b>Delete Time</b> - Seconds until deletion
• <b>Delete Message</b> - Warning text
• <b>Success Message</b> - Confirmation text

<i>Current Timer:</i> <code>{time}s</code> ({mins} min)
<i>Status:</i> <code>{status}</code>
"""

ADVANCED_MENU = """
⚙️ <b>ADVANCED SETTINGS</b>

Additional configuration options:

• <b>View All Settings</b> - Complete overview
• <b>Reset to Defaults</b> - Clear all settings
• <b>Backup Settings</b> - Export configuration

<i>Use these options carefully!</i>
"""

# ===========================
# KEYBOARD BUILDERS
# ===========================

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 Appearance", callback_data="menu_appearance"),
            InlineKeyboardButton("📢 Force Sub", callback_data="menu_forcesub")
        ],
        [
            InlineKeyboardButton("📝 Captions", callback_data="menu_captions"),
            InlineKeyboardButton("🔒 Protection", callback_data="menu_protection")
        ],
        [
            InlineKeyboardButton("⏱️ Auto Delete", callback_data="menu_autodelete"),
            InlineKeyboardButton("⚙️ Advanced", callback_data="menu_advanced")
        ],
        [
            InlineKeyboardButton("📊 View All Settings", callback_data="view_all"),
            InlineKeyboardButton("📚 Help", callback_data="show_help")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="menu_main"),
            InlineKeyboardButton("❌ Close", callback_data="close_panel")
        ]
    ])

def appearance_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Start Message", callback_data="edit_start_msg"),
            InlineKeyboardButton("🖼️ Start Picture", callback_data="edit_start_pic")
        ],
        [
            InlineKeyboardButton("📊 Stats Text", callback_data="edit_stats_text")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
        ]
    ])

def forcesub_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🆔 Channel ID", callback_data="edit_force_channel"),
            InlineKeyboardButton("💬 Force Message", callback_data="edit_force_msg")
        ],
        [
            InlineKeyboardButton("🔄 Join Request", callback_data="toggle_join_request")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
        ]
    ])

def captions_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 Custom Caption", callback_data="edit_caption"),
            InlineKeyboardButton("💭 User Reply", callback_data="edit_user_reply")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
        ]
    ])

def protection_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔒 Protect Content", callback_data="toggle_protect"),
            InlineKeyboardButton("🔘 Channel Button", callback_data="toggle_channel_btn")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
        ]
    ])

def autodelete_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱️ Delete Time", callback_data="edit_autodel_time"),
            InlineKeyboardButton("💬 Delete Message", callback_data="edit_autodel_msg")
        ],
        [
            InlineKeyboardButton("✅ Success Message", callback_data="edit_autodel_success")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
        ]
    ])

def advanced_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👁️ View All", callback_data="view_all"),
            InlineKeyboardButton("🔄 Reset All", callback_data="confirm_reset")
        ],
        [
            InlineKeyboardButton("💾 Backup Config", callback_data="backup_config"),
            InlineKeyboardButton("📥 Restore Config", callback_data="restore_config")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
        ]
    ])

def back_keyboard(menu: str = "main"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=f"menu_{menu}")]
    ])

def toggle_keyboard(current_value: bool, callback_prefix: str):
    status = "✅ Enabled" if current_value else "❌ Disabled"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"Currently: {status}",
                callback_data="noop"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Enable" if not current_value else "✅ Enabled ✓",
                callback_data=f"{callback_prefix}_true" if not current_value else "noop"
            ),
            InlineKeyboardButton(
                "❌ Disable" if current_value else "❌ Disabled ✓",
                callback_data=f"{callback_prefix}_false" if current_value else "noop"
            )
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_main")
        ]
    ])

# ===========================
# HELPER FUNCTIONS
# ===========================

async def safe_get_setting(key: str, default=None):
    """Safely get a setting with error handling"""
    try:
        return get_setting(key, default)
    except Exception as e:
        print(f"Error getting setting {key}: {e}")
        return default

async def safe_update_setting(key: str, value):
    """Safely update a setting with error handling"""
    try:
        update_setting(key, value)
        return True
    except Exception as e:
        print(f"Error updating setting {key}: {e}")
        return False

async def get_force_sub_info():
    """Get formatted force sub information"""
    channel_id = await safe_get_setting('force_channel', '0')
    join_req = await safe_get_setting('join_request', 'False')
    return channel_id, join_req

async def get_protection_info():
    """Get formatted protection information"""
    protect = await safe_get_setting('protect_content', 'False')
    button = await safe_get_setting('disable_channel_button', 'False')
    return protect, button

async def get_autodelete_info():
    """Get formatted auto-delete information"""
    time = await safe_get_setting('auto_delete_time', '0')
    try:
        time_int = int(time)
        mins = time_int // 60
        status = "✅ Enabled" if time_int > 0 else "❌ Disabled"
        return time, mins, status
    except:
        return '0', 0, "❌ Disabled"

async def listen_for_input(client: Client, chat_id: int, timeout: int = 120) -> Optional[Message]:
    """Listen for user input with timeout and cancellation"""
    try:
        response = await client.listen(chat_id, timeout=timeout)
        if response.text and response.text.lower() in ['cancel', '/cancel', 'stop', '/stop']:
            return None
        return response
    except asyncio.TimeoutError:
        return None

# ===========================
# COMMAND PARSER
# ===========================

def parse_setup_command(text: str):
    """Parse setup command and return command type"""
    parts = text.split(maxsplit=2)
    if len(parts) == 1:
        return None, None
    elif len(parts) == 2:
        return parts[1].lower(), None
    else:
        return parts[1].lower(), parts[2]

# ===========================
# MAIN COMMAND HANDLERS
# ===========================

@Bot.on_message(filters.command('setup') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def setup_command(client: Bot, message: Message):
    """Main setup command handler - supports both panel and direct commands"""
    try:
        command, arg = parse_setup_command(message.text)
        
        # No subcommand - show interactive panel
        if command is None:
            await message.reply_text(
                MAIN_MENU_TEXT,
                reply_markup=main_menu_keyboard(),
                quote=True
            )
            return
        
        # Help command
        if command in ['help', 'commands', '?']:
            await message.reply_text(HELP_TEXT, quote=True)
            return
        
        # View all settings
        if command in ['view', 'show', 'list']:
            await show_all_settings_command(client, message)
            return
        
        # Backup command
        if command in ['backup', 'export']:
            await backup_config_command(client, message)
            return
        
        # Restore command
        if command in ['restore', 'import']:
            await restore_config_command(client, message)
            return
        
        # Reset command
        if command in ['reset', 'clear']:
            await reset_config_command(client, message)
            return
        
        # Direct edit commands
        edit_commands = {
            'start_msg': ('start_msg', 'start message', 'appearance'),
            'start_pic': ('start_pic', 'start picture', 'appearance'),
            'stats_text': ('stats_text', 'stats text', 'appearance'),
            'force_channel': ('force_channel', 'force channel', 'forcesub'),
            'force_msg': ('force_msg', 'force message', 'forcesub'),
            'join_request': ('join_request', 'join request', 'forcesub'),
            'caption': ('caption', 'custom caption', 'captions'),
            'user_reply': ('user_reply', 'user reply', 'captions'),
            'protect': ('protect', 'content protection', 'protection'),
            'channel_btn': ('channel_btn', 'channel button', 'protection'),
            'autodel_time': ('autodel_time', 'auto delete time', 'autodelete'),
            'autodel_msg': ('autodel_msg', 'auto delete message', 'autodelete'),
            'autodel_success': ('autodel_success', 'success message', 'autodelete'),
        }
        
        if command in edit_commands:
            key, name, menu = edit_commands[command]
            await handle_direct_edit(client, message, key, name, menu)
            return
        
        # Unknown command
        await message.reply_text(
            f"❌ <b>Unknown command:</b> <code>{command}</code>\n\n"
            f"Use <code>/setup help</code> to see all available commands.",
            quote=True
        )
    
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Error:</b> {str(e)}\n\n"
            f"Use <code>/setup help</code> for command guide.",
            quote=True
        )

# ===========================
# DIRECT COMMAND HANDLERS
# ===========================

async def handle_direct_edit(client: Bot, message: Message, key: str, name: str, menu: str):
    """Handle direct edit commands"""
    if key == 'start_msg':
        await edit_start_message_cmd(client, message)
    elif key == 'start_pic':
        await edit_start_pic_cmd(client, message)
    elif key == 'stats_text':
        await edit_stats_text_cmd(client, message)
    elif key == 'force_channel':
        await edit_force_channel_cmd(client, message)
    elif key == 'force_msg':
        await edit_force_message_cmd(client, message)
    elif key == 'join_request':
        await toggle_join_request_cmd(client, message)
    elif key == 'caption':
        await edit_caption_cmd(client, message)
    elif key == 'user_reply':
        await edit_user_reply_cmd(client, message)
    elif key == 'protect':
        await toggle_protect_content_cmd(client, message)
    elif key == 'channel_btn':
        await toggle_channel_button_cmd(client, message)
    elif key == 'autodel_time':
        await edit_autodel_time_cmd(client, message)
    elif key == 'autodel_msg':
        await edit_autodel_msg_cmd(client, message)
    elif key == 'autodel_success':
        await edit_autodel_success_cmd(client, message)

async def show_all_settings_command(client: Bot, message: Message):
    """Show all settings via command"""
    try:
        start_msg = await safe_get_setting('start_msg', 'Not Set')
        start_pic = await safe_get_setting('start_pic', 'Not Set')
        force_msg = await safe_get_setting('force_msg', 'Not Set')
        force_channel = await safe_get_setting('force_channel', '0')
        caption = await safe_get_setting('caption', 'Not Set')
        protect = await safe_get_setting('protect_content', 'False')
        autodel_time = await safe_get_setting('auto_delete_time', '0')
        autodel_msg = await safe_get_setting('auto_delete_msg', 'Not Set')
        autodel_success = await safe_get_setting('auto_delete_success', 'Not Set')
        channel_btn = await safe_get_setting('disable_channel_button', 'False')
        user_reply = await safe_get_setting('user_reply', 'Not Set')
        stats_text = await safe_get_setting('stats_text', 'Not Set')
        join_req = await safe_get_setting('join_request', 'False')
        
        def truncate(text, length=50):
            text = str(text)
            return text[:length] + '...' if len(text) > length else text
        
        settings_text = f"""
╔══════════════════════════════╗
║  📋 <b>ALL BOT SETTINGS</b>  📋  ║
╚══════════════════════════════╝

🎨 <b>APPEARANCE</b>
├ Start Message: <code>{truncate(start_msg, 40)}</code>
├ Start Picture: <code>{truncate(start_pic, 40)}</code>
└ Stats Text: <code>{truncate(stats_text, 40)}</code>

📢 <b>FORCE SUBSCRIBE</b>
├ Channel ID: <code>{force_channel}</code>
├ Join Request: <code>{join_req}</code>
└ Force Message: <code>{truncate(force_msg, 40)}</code>

📝 <b>CAPTIONS & REPLIES</b>
├ Custom Caption: <code>{truncate(caption, 40)}</code>
└ User Reply: <code>{truncate(user_reply, 40)}</code>

🔒 <b>PROTECTION</b>
├ Protect Content: <code>{protect}</code>
└ Channel Button: <code>{'Hidden' if channel_btn == 'True' else 'Visible'}</code>

⏱️ <b>AUTO DELETE</b>
├ Delete Time: <code>{autodel_time}s</code>
├ Delete Message: <code>{truncate(autodel_msg, 40)}</code>
└ Success Message: <code>{truncate(autodel_success, 40)}</code>

<i>Use /setup [command] to edit any setting</i>
"""
        
        await message.reply_text(settings_text, quote=True)
    except Exception as e:
        await message.reply_text(f"❌ <b>Error:</b> {str(e)}", quote=True)

async def backup_config_command(client: Bot, message: Message):
    """Backup configuration via command"""
    try:
        settings_keys = [
            'start_msg', 'start_pic', 'force_msg', 'force_channel',
            'caption', 'protect_content', 'auto_delete_time', 'auto_delete_msg',
            'auto_delete_success', 'disable_channel_button', 'user_reply',
            'stats_text', 'join_request'
        ]
        
        backup_data = {}
        for key in settings_keys:
            backup_data[key] = await safe_get_setting(key, 'Not Set')
        
        import json
        from datetime import datetime
        backup_json = json.dumps(backup_data, indent=2)
        
        await message.reply_document(
            document=backup_json.encode(),
            file_name=f"bot_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            caption="✅ <b>Configuration Backup</b>\n\nUse <code>/setup restore</code> to restore.",
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"❌ <b>Backup failed:</b> {str(e)}", quote=True)

async def restore_config_command(client: Bot, message: Message):
    """Restore configuration via command"""
    msg = await message.reply_text(
        "📥 <b>Restore Configuration</b>\n\n"
        "Reply to this message with the backup JSON file.\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    
    response = await listen_for_input(client, message.chat.id, 60)
    
    if response is None or not response.document:
        await msg.edit_text("❌ <b>Cancelled or invalid file!</b>")
        return
    
    try:
        import json
        file_path = await response.download()
        with open(file_path, 'r') as f:
            backup_data = json.load(f)
        
        count = 0
        for key, value in backup_data.items():
            if value != 'Not Set':
                if await safe_update_setting(key, value):
                    count += 1
        
        await response.reply_text(
            f"✅ <b>Configuration restored!</b>\n\n"
            f"<b>Restored {count}/{len(backup_data)} settings successfully.</b>",
            quote=True
        )
    except Exception as e:
        await response.reply_text(f"❌ <b>Restore failed:</b> {str(e)}", quote=True)

async def reset_config_command(client: Bot, message: Message):
    """Reset configuration via command"""
    msg = await message.reply_text(
        "⚠️ <b>RESET ALL SETTINGS</b>\n\n"
        "Are you sure? This will delete ALL custom settings!\n\n"
        "Reply with <code>YES</code> to confirm or <code>NO</code> to cancel.",
        quote=True
    )
    
    response = await listen_for_input(client, message.chat.id, 30)
    
    if response is None or response.text.upper() != 'YES':
        await msg.edit_text("❌ <b>Reset cancelled.</b>")
        return
    
    try:
        from database.database import database
        if hasattr(database, 'settings_collection'):
            database.settings_collection.delete_many({})
        
        await response.reply_text(
            "✅ <b>All settings have been reset!</b>\n\n"
            "<i>Bot will now use environment variables.</i>",
            quote=True
        )
    except Exception as e:
        await response.reply_text(f"❌ <b>Reset failed:</b> {str(e)}", quote=True)

# Command-specific edit functions (shortened versions)
async def edit_start_message_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "💬 <b>Edit Start Message</b>\n\nSend the new message.\n\n"
        "<b>Placeholders:</b> <code>{first} {last} {username} {mention} {id}</code>\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response and await safe_update_setting('start_msg', response.text):
        await response.reply_text(f"✅ <b>Updated!</b>\n\n{response.text[:200]}", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled or failed!</b>")

async def edit_start_pic_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "🖼️ <b>Edit Start Picture</b>\n\nSend image URL or <code>none</code> to remove.\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id, 60)
    if response:
        value = '' if response.text.lower() == 'none' else response.text
        if await safe_update_setting('start_pic', value):
            await response.reply_text(f"✅ <b>{'Removed' if not value else 'Updated'}!</b>", quote=True)
        else:
            await response.reply_text("❌ <b>Failed!</b>", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled!</b>")

async def edit_stats_text_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "📊 <b>Edit Stats Text</b>\n\nSend the format.\n\n"
        "<b>Placeholder:</b> <code>{uptime}</code>\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response and await safe_update_setting('stats_text', response.text):
        await response.reply_text(f"✅ <b>Updated!</b>\n\n{response.text}", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled or failed!</b>")

async def edit_force_channel_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "🆔 <b>Edit Force Channel</b>\n\nSend channel ID or <code>0</code> to disable.\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id, 60)
    if response:
        try:
            channel_id = int(response.text)
            if channel_id != 0:
                chat = await client.get_chat(channel_id)
                if await safe_update_setting('force_channel', str(channel_id)):
                    await response.reply_text(f"✅ <b>Updated!</b>\n\n{chat.title} ({channel_id})", quote=True)
                else:
                    await response.reply_text("❌ <b>Failed!</b>", quote=True)
            else:
                if await safe_update_setting('force_channel', '0'):
                    await response.reply_text("✅ <b>Force subscribe disabled!</b>", quote=True)
        except ValueError:
            await response.reply_text("❌ <b>Invalid ID!</b>", quote=True)
        except Exception as e:
            await response.reply_text(f"❌ <b>Error:</b> {str(e)}", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled!</b>")

async def edit_force_message_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "💬 <b>Edit Force Message</b>\n\nSend the message.\n\n"
        "<b>Placeholders:</b> <code>{first} {last} {username} {mention} {id}</code>\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response and await safe_update_setting('force_msg', response.text):
        await response.reply_text(f"✅ <b>Updated!</b>\n\n{response.text[:200]}", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled or failed!</b>")

async def toggle_join_request_cmd(client: Bot, message: Message):
    current = await safe_get_setting('join_request', 'False')
    new_value = 'False' if current == 'True' else 'True'
    if await safe_update_setting('join_request', new_value):
        await message.reply_text(
            f"✅ <b>Join Request {'Enabled' if new_value == 'True' else 'Disabled'}!</b>",
            quote=True
        )
    else:
        await message.reply_text("❌ <b>Failed to update!</b>", quote=True)

async def edit_caption_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "📄 <b>Edit Caption</b>\n\nSend caption or <code>none</code> to disable.\n\n"
        "<b>Placeholders:</b> <code>{filename} {previouscaption}</code>\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response:
        value = '' if response.text.lower() == 'none' else response.text
        if await safe_update_setting('caption', value):
            await response.reply_text(f"✅ <b>{'Disabled' if not value else 'Updated'}!</b>", quote=True)
        else:
            await response.reply_text("❌ <b>Failed!</b>", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled!</b>")

async def edit_user_reply_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "💭 <b>Edit User Reply</b>\n\nSend auto-reply or <code>none</code> to disable.\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response:
        value = '' if response.text.lower() == 'none' else response.text
        if await safe_update_setting('user_reply', value):
            await response.reply_text(f"✅ <b>{'Disabled' if not value else 'Updated'}!</b>", quote=True)
        else:
            await response.reply_text("❌ <b>Failed!</b>", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled!</b>")

async def toggle_protect_content_cmd(client: Bot, message: Message):
    current = await safe_get_setting('protect_content', 'False')
    new_value = 'False' if current == 'True' else 'True'
    if await safe_update_setting('protect_content', new_value):
        await message.reply_text(
            f"✅ <b>Content Protection {'Enabled' if new_value == 'True' else 'Disabled'}!</b>",
            quote=True
        )
    else:
        await message.reply_text("❌ <b>Failed to update!</b>", quote=True)

async def toggle_channel_button_cmd(client: Bot, message: Message):
    current = await safe_get_setting('disable_channel_button', 'False')
    new_value = 'False' if current == 'True' else 'True'
    if await safe_update_setting('disable_channel_button', new_value):
        await message.reply_text(
            f"✅ <b>Channel Button {'Hidden' if new_value == 'True' else 'Visible'}!</b>",
            quote=True
        )
    else:
        await message.reply_text("❌ <b>Failed to update!</b>", quote=True)

async def edit_autodel_time_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "⏱️ <b>Edit Auto Delete Time</b>\n\nSend seconds or <code>0</code> to disable.\n\n"
        "<b>Examples:</b> 300 (5min), 600 (10min), 1800 (30min)\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id, 60)
    if response:
        try:
            seconds = int(response.text)
            if seconds < 0:
                raise ValueError()
            if await safe_update_setting('auto_delete_time', str(seconds)):
                await response.reply_text(
                    f"✅ <b>{'Disabled' if seconds == 0 else f'Updated to {seconds}s ({seconds//60}min)'}!</b>",
                    quote=True
                )
            else:
                await response.reply_text("❌ <b>Failed!</b>", quote=True)
        except ValueError:
            await response.reply_text("❌ <b>Invalid number!</b>", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled!</b>")

async def edit_autodel_msg_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "💬 <b>Edit Delete Message</b>\n\nSend warning message.\n\n"
        "<b>Placeholder:</b> <code>{time}</code>\n\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response and await safe_update_setting('auto_delete_msg', response.text):
        await response.reply_text(f"✅ <b>Updated!</b>\n\n{response.text[:200]}", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled or failed!</b>")

async def edit_autodel_success_cmd(client: Bot, message: Message):
    msg = await message.reply_text(
        "✅ <b>Edit Success Message</b>\n\nSend success message.\n"
        "Send <code>cancel</code> to abort.",
        quote=True
    )
    response = await listen_for_input(client, message.chat.id)
    if response and await safe_update_setting('auto_delete_success', response.text):
        await response.reply_text(f"✅ <b>Updated!</b>\n\n{response.text}", quote=True)
    else:
        await msg.edit_text("❌ <b>Cancelled or failed!</b>")

# ===========================
# MENU NAVIGATION HANDLERS (Panel Mode)
# ===========================

@Bot.on_callback_query(filters.regex(r'^menu_'))
async def menu_handler(client: Bot, query: CallbackQuery):
    """Handle menu navigation"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this panel!", show_alert=True)
        return
    
    try:
        menu_type = query.data.split('_')[1]
        
        if menu_type == "main":
            await query.edit_message_text(
                MAIN_MENU_TEXT,
                reply_markup=main_menu_keyboard()
            )
        
        elif menu_type == "appearance":
            await query.edit_message_text(
                APPEARANCE_MENU,
                reply_markup=appearance_keyboard()
            )
        
        elif menu_type == "forcesub":
            channel_id, join_req = await get_force_sub_info()
            text = FORCE_SUB_MENU.format(channel=channel_id, join_req=join_req)
            await query.edit_message_text(
                text,
                reply_markup=forcesub_keyboard()
            )
        
        elif menu_type == "captions":
            await query.edit_message_text(
                CAPTIONS_MENU,
                reply_markup=captions_keyboard()
            )
        
        elif menu_type == "protection":
            protect, button = await get_protection_info()
            text = PROTECTION_MENU.format(
                protect="Enabled" if protect == 'True' else "Disabled",
                button="Hidden" if button == 'True' else "Visible"
            )
            await query.edit_message_text(
                text,
                reply_markup=protection_keyboard()
            )
        
        elif menu_type == "autodelete":
            time, mins, status = await get_autodelete_info()
            text = AUTO_DELETE_MENU.format(time=time, mins=mins, status=status)
            await query.edit_message_text(
                text,
                reply_markup=autodelete_keyboard()
            )
        
        elif menu_type == "advanced":
            await query.edit_message_text(
                ADVANCED_MENU,
                reply_markup=advanced_keyboard()
            )
        
        await query.answer()
    
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)

# ===========================
# EDIT HANDLERS (Panel Mode)
# ===========================

@Bot.on_callback_query(filters.regex(r'^edit_'))
async def edit_handler(client: Bot, query: CallbackQuery):
    """Handle edit requests from panel"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    edit_type = query.data.split('_', 1)[1]
    
    try:
        if edit_type == "start_msg":
            await edit_start_message(client, query)
        elif edit_type == "start_pic":
            await edit_start_pic(client, query)
        elif edit_type == "stats_text":
            await edit_stats_text(client, query)
        elif edit_type == "force_channel":
            await edit_force_channel(client, query)
        elif edit_type == "force_msg":
            await edit_force_message(client, query)
        elif edit_type == "caption":
            await edit_caption(client, query)
        elif edit_type == "user_reply":
            await edit_user_reply(client, query)
        elif edit_type == "autodel_time":
            await edit_autodel_time(client, query)
        elif edit_type == "autodel_msg":
            await edit_autodel_msg(client, query)
        elif edit_type == "autodel_success":
            await edit_autodel_success(client, query)
    except Exception as e:
        await query.message.reply_text(
            f"❌ <b>Error:</b> {str(e)}\n\nOperation cancelled."
        )

# Panel edit functions (same as before)
async def edit_start_message(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "💬 <b>Edit Start Message</b>\n\n"
        "Send me the new start message.\n\n"
        "<b>Available placeholders:</b>\n"
        "• <code>{first}</code> - First name\n"
        "• <code>{last}</code> - Last name\n"
        "• <code>{username}</code> - Username\n"
        "• <code>{mention}</code> - Mention user\n"
        "• <code>{id}</code> - User ID\n\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("appearance")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>\n\nStart message was not updated.",
            reply_markup=back_keyboard("appearance")
        )
        return
    
    if await safe_update_setting('start_msg', response.text):
        await response.reply_text(
            f"✅ <b>Start message updated successfully!</b>\n\n"
            f"<b>Preview:</b>\n{response.text[:200]}{'...' if len(response.text) > 200 else ''}",
            reply_markup=back_keyboard("appearance")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update start message!</b>\n\nPlease try again.",
            reply_markup=back_keyboard("appearance")
        )

async def edit_start_pic(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "🖼️ <b>Edit Start Picture</b>\n\n"
        "Send me the image URL.\n\n"
        "Send <code>none</code> to remove the picture.\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("appearance")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id, 60)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("appearance")
        )
        return
    
    value = '' if response.text.lower() == 'none' else response.text
    
    if await safe_update_setting('start_pic', value):
        status = "removed" if value == '' else "updated"
        await response.reply_text(
            f"✅ <b>Start picture {status}!</b>\n\n"
            f"{'<i>No picture will be shown.</i>' if value == '' else f'<b>URL:</b> <code>{value[:100]}</code>'}",
            reply_markup=back_keyboard("appearance")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("appearance")
        )

async def edit_stats_text(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "📊 <b>Edit Stats Text</b>\n\n"
        "Send me the stats message format.\n\n"
        "<b>Available placeholder:</b>\n"
        "• <code>{uptime}</code> - Bot uptime\n\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("appearance")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("appearance")
        )
        return
    
    if await safe_update_setting('stats_text', response.text):
        await response.reply_text(
            f"✅ <b>Stats text updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            reply_markup=back_keyboard("appearance")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("appearance")
        )

async def edit_force_channel(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "🆔 <b>Edit Force Subscribe Channel</b>\n\n"
        "Send me the channel ID (e.g., <code>-1001234567890</code>)\n\n"
        "Send <code>0</code> to disable force subscribe.\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("forcesub")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id, 60)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("forcesub")
        )
        return
    
    try:
        channel_id = int(response.text)
        
        if channel_id != 0:
            try:
                chat = await client.get_chat(channel_id)
                if await safe_update_setting('force_channel', str(channel_id)):
                    await response.reply_text(
                        f"✅ <b>Force subscribe channel updated!</b>\n\n"
                        f"<b>Channel:</b> {chat.title}\n"
                        f"<b>ID:</b> <code>{channel_id}</code>",
                        reply_markup=back_keyboard("forcesub")
                    )
                else:
                    raise Exception("Failed to save setting")
            except Exception as e:
                await response.reply_text(
                    f"❌ <b>Error:</b> {str(e)}\n\n"
                    f"Make sure the bot is admin in the channel!",
                    reply_markup=back_keyboard("forcesub")
                )
        else:
            if await safe_update_setting('force_channel', '0'):
                await response.reply_text(
                    "✅ <b>Force subscribe disabled!</b>",
                    reply_markup=back_keyboard("forcesub")
                )
            else:
                await response.reply_text(
                    "❌ <b>Failed to update!</b>",
                    reply_markup=back_keyboard("forcesub")
                )
    except ValueError:
        await response.reply_text(
            "❌ <b>Invalid channel ID!</b>\n\nPlease send a valid number.",
            reply_markup=back_keyboard("forcesub")
        )

async def edit_force_message(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "💬 <b>Edit Force Subscribe Message</b>\n\n"
        "Send me the force subscribe message.\n\n"
        "<b>Available placeholders:</b>\n"
        "• <code>{first}</code>, <code>{last}</code>, <code>{username}</code>\n"
        "• <code>{mention}</code>, <code>{id}</code>\n\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("forcesub")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("forcesub")
        )
        return
    
    if await safe_update_setting('force_msg', response.text):
        await response.reply_text(
            f"✅ <b>Force message updated!</b>\n\n<b>Preview:</b>\n{response.text[:200]}",
            reply_markup=back_keyboard("forcesub")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("forcesub")
        )

async def edit_caption(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "📄 <b>Edit Custom Caption</b>\n\n"
        "Send me the custom caption for files.\n\n"
        "<b>Available placeholders:</b>\n"
        "• <code>{filename}</code> - File name\n"
        "• <code>{previouscaption}</code> - Original caption\n\n"
        "Send <code>none</code> to disable custom caption.\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("captions")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("captions")
        )
        return
    
    value = '' if response.text.lower() == 'none' else response.text
    
    if await safe_update_setting('caption', value):
        status = "disabled" if value == '' else "updated"
        await response.reply_text(
            f"✅ <b>Custom caption {status}!</b>\n\n"
            f"{'<i>Default captions will be used.</i>' if value == '' else f'<b>Preview:</b>\n{value[:200]}'}",
            reply_markup=back_keyboard("captions")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("captions")
        )

async def edit_user_reply(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "💭 <b>Edit User Reply Text</b>\n\n"
        "Send me the auto-reply message for user DMs.\n\n"
        "Send <code>none</code> to disable auto-reply.\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("captions")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("captions")
        )
        return
    
    value = '' if response.text.lower() == 'none' else response.text
    
    if await safe_update_setting('user_reply', value):
        status = "disabled" if value == '' else "updated"
        await response.reply_text(
            f"✅ <b>User reply {status}!</b>\n\n"
            f"{'<i>No auto-reply will be sent.</i>' if value == '' else f'<b>Preview:</b>\n{value}'}",
            reply_markup=back_keyboard("captions")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("captions")
        )

async def edit_autodel_time(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "⏱️ <b>Edit Auto Delete Time</b>\n\n"
        "Send me the time in seconds for auto-deletion.\n\n"
        "<b>Examples:</b>\n"
        "• <code>300</code> - 5 minutes\n"
        "• <code>600</code> - 10 minutes\n"
        "• <code>1800</code> - 30 minutes\n\n"
        "Send <code>0</code> to disable.\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("autodelete")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id, 60)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("autodelete")
        )
        return
    
    try:
        seconds = int(response.text)
        if seconds < 0:
            raise ValueError("Negative values not allowed")
        
        if await safe_update_setting('auto_delete_time', str(seconds)):
            mins = seconds // 60
            if seconds == 0:
                await response.reply_text(
                    "✅ <b>Auto-delete disabled!</b>",
                    reply_markup=back_keyboard("autodelete")
                )
            else:
                await response.reply_text(
                    f"✅ <b>Auto-delete time updated!</b>\n\n"
                    f"<b>Time:</b> {seconds}s ({mins} minutes)",
                    reply_markup=back_keyboard("autodelete")
                )
        else:
            await response.reply_text(
                "❌ <b>Failed to update!</b>",
                reply_markup=back_keyboard("autodelete")
            )
    except ValueError:
        await response.reply_text(
            "❌ <b>Invalid number!</b>\n\nPlease send a valid positive number.",
            reply_markup=back_keyboard("autodelete")
        )

async def edit_autodel_msg(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "💬 <b>Edit Auto Delete Message</b>\n\n"
        "Send me the warning message before deletion.\n\n"
        "<b>Available placeholder:</b>\n"
        "• <code>{time}</code> - Seconds remaining\n\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("autodelete")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("autodelete")
        )
        return
    
    if await safe_update_setting('auto_delete_msg', response.text):
        await response.reply_text(
            f"✅ <b>Delete message updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            reply_markup=back_keyboard("autodelete")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("autodelete")
        )

async def edit_autodel_success(client: Bot, query: CallbackQuery):
    await query.message.edit_text(
        "✅ <b>Edit Success Message</b>\n\n"
        "Send me the message after successful deletion.\n\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("autodelete")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id)
    
    if response is None:
        await query.message.edit_text(
            "❌ <b>Cancelled!</b>",
            reply_markup=back_keyboard("autodelete")
        )
        return
    
    if await safe_update_setting('auto_delete_success', response.text):
        await response.reply_text(
            f"✅ <b>Success message updated!</b>\n\n<b>Preview:</b>\n{response.text}",
            reply_markup=back_keyboard("autodelete")
        )
    else:
        await response.reply_text(
            "❌ <b>Failed to update!</b>",
            reply_markup=back_keyboard("autodelete")
        )

# ===========================
# TOGGLE HANDLERS
# ===========================

@Bot.on_callback_query(filters.regex(r'^toggle_'))
async def toggle_handler(client: Bot, query: CallbackQuery):
    """Handle toggle switches"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    toggle_type = query.data.split('_', 1)[1]
    
    try:
        if toggle_type == "protect":
            await toggle_protect_content(client, query)
        elif toggle_type == "channel_btn":
            await toggle_channel_button(client, query)
        elif toggle_type == "join_request":
            await toggle_join_request(client, query)
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)

async def toggle_protect_content(client: Bot, query: CallbackQuery):
    current = await safe_get_setting('protect_content', 'False')
    current_bool = (current == 'True')
    
    await query.message.edit_text(
        "🔒 <b>PROTECT CONTENT</b>\n\n"
        "Prevent users from forwarding files from the bot.\n\n"
        f"<b>Current Status:</b> {'✅ Enabled' if current_bool else '❌ Disabled'}\n\n"
        "<i>Choose an option:</i>",
        reply_markup=toggle_keyboard(current_bool, "set_protect")
    )
    await query.answer()

async def toggle_channel_button(client: Bot, query: CallbackQuery):
    current = await safe_get_setting('disable_channel_button', 'False')
    current_bool = (current == 'True')
    
    await query.message.edit_text(
        "🔘 <b>CHANNEL SHARE BUTTON</b>\n\n"
        "Show or hide the share button on channel posts.\n\n"
        f"<b>Current Status:</b> {'❌ Hidden' if current_bool else '✅ Visible'}\n\n"
        "<i>Choose an option:</i>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"Currently: {'Hidden' if current_bool else 'Visible'}",
                    callback_data="noop"
                )
            ],
            [
                InlineKeyboardButton(
                    "👁️ Show Button" if current_bool else "👁️ Showing ✓",
                    callback_data="set_channel_btn_false" if current_bool else "noop"
                ),
                InlineKeyboardButton(
                    "🙈 Hide Button" if not current_bool else "🙈 Hidden ✓",
                    callback_data="set_channel_btn_true" if not current_bool else "noop"
                )
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="menu_protection")
            ]
        ])
    )
    await query.answer()

async def toggle_join_request(client: Bot, query: CallbackQuery):
    current = await safe_get_setting('join_request', 'False')
    current_bool = (current == 'True')
    
    await query.message.edit_text(
        "📝 <b>JOIN REQUEST MODE</b>\n\n"
        "Use join request instead of direct channel join.\n\n"
        f"<b>Current Status:</b> {'✅ Enabled' if current_bool else '❌ Disabled'}\n\n"
        "<i>Choose an option:</i>",
        reply_markup=toggle_keyboard(current_bool, "set_join_req")
    )
    await query.answer()

# ===========================
# SETTING UPDATE HANDLERS
# ===========================

@Bot.on_callback_query(filters.regex(r'^set_'))
async def set_handler(client: Bot, query: CallbackQuery):
    """Handle setting updates"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    try:
        parts = query.data.split('_')
        if len(parts) < 3:
            await query.answer("❌ Invalid callback data!", show_alert=True)
            return
        
        setting_type = '_'.join(parts[1:-1])
        value = parts[-1]
        
        if setting_type == "protect":
            success = await safe_update_setting('protect_content', value.capitalize())
            if success:
                await query.answer(f"✅ Content protection {'enabled' if value == 'true' else 'disabled'}!", show_alert=True)
                await query.message.edit_text(
                    f"✅ <b>Protection Updated!</b>\n\n"
                    f"Content protection is now <b>{'enabled' if value == 'true' else 'disabled'}</b>.",
                    reply_markup=back_keyboard("protection")
                )
            else:
                await query.answer("❌ Failed to update setting!", show_alert=True)
        
        elif setting_type == "channel_btn":
            success = await safe_update_setting('disable_channel_button', value.capitalize())
            if success:
                await query.answer(f"✅ Channel button {'hidden' if value == 'true' else 'visible'}!", show_alert=True)
                await query.message.edit_text(
                    f"✅ <b>Button Updated!</b>\n\n"
                    f"Channel share button is now <b>{'hidden' if value == 'true' else 'visible'}</b>.",
                    reply_markup=back_keyboard("protection")
                )
            else:
                await query.answer("❌ Failed to update setting!", show_alert=True)
        
        elif setting_type == "join_req":
            success = await safe_update_setting('join_request', value.capitalize())
            if success:
                await query.answer(f"✅ Join request {'enabled' if value == 'true' else 'disabled'}!", show_alert=True)
                await query.message.edit_text(
                    f"✅ <b>Join Request Updated!</b>\n\n"
                    f"Join request mode is now <b>{'enabled' if value == 'true' else 'disabled'}</b>.",
                    reply_markup=back_keyboard("forcesub")
                )
            else:
                await query.answer("❌ Failed to update setting!", show_alert=True)
    
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)

# ===========================
# VIEW ALL SETTINGS
# ===========================

@Bot.on_callback_query(filters.regex(r'^view_all'))  
async def view_all_settings(client: Bot, query: CallbackQuery):
    """Display all current settings"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    try:
        # Fetch all settings
        start_msg = await safe_get_setting('start_msg', 'Not Set')
        start_pic = await safe_get_setting('start_pic', 'Not Set')
        force_msg = await safe_get_setting('force_msg', 'Not Set')
        force_channel = await safe_get_setting('force_channel', '0')
        caption = await safe_get_setting('caption', 'Not Set')
        protect = await safe_get_setting('protect_content', 'False')
        autodel_time = await safe_get_setting('auto_delete_time', '0')
        autodel_msg = await safe_get_setting('auto_delete_msg', 'Not Set')
        autodel_success = await safe_get_setting('auto_delete_success', 'Not Set')
        channel_btn = await safe_get_setting('disable_channel_button', 'False')
        user_reply = await safe_get_setting('user_reply', 'Not Set')
        stats_text = await safe_get_setting('stats_text', 'Not Set')
        join_req = await safe_get_setting('join_request', 'False')
        
        # Format the display
        def truncate(text, length=50):
            text = str(text)
            return text[:length] + '...' if len(text) > length else text
        
        settings_text = f"""
╔══════════════════════════════╗
║  📋 <b>ALL BOT SETTINGS</b>  📋  ║
╚══════════════════════════════╝

🎨 <b>APPEARANCE</b>
├ Start Message: <code>{truncate(start_msg, 40)}</code>
├ Start Picture: <code>{truncate(start_pic, 40)}</code>
└ Stats Text: <code>{truncate(stats_text, 40)}</code>

📢 <b>FORCE SUBSCRIBE</b>
├ Channel ID: <code>{force_channel}</code>
├ Join Request: <code>{join_req}</code>
└ Force Message: <code>{truncate(force_msg, 40)}</code>

📝 <b>CAPTIONS & REPLIES</b>
├ Custom Caption: <code>{truncate(caption, 40)}</code>
└ User Reply: <code>{truncate(user_reply, 40)}</code>

🔒 <b>PROTECTION</b>
├ Protect Content: <code>{protect}</code>
└ Channel Button: <code>{'Hidden' if channel_btn == 'True' else 'Visible'}</code>

⏱️ <b>AUTO DELETE</b>
├ Delete Time: <code>{autodel_time}s</code>
├ Delete Message: <code>{truncate(autodel_msg, 40)}</code>
└ Success Message: <code>{truncate(autodel_success, 40)}</code>

<i>Last updated: Now</i>
"""
        
        await query.message.edit_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💾 Backup Config", callback_data="backup_config"),
                    InlineKeyboardButton("🔄 Refresh", callback_data="view_all")
                ],
                [
                    InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")
                ]
            ])
        )
        await query.answer("✅ Settings loaded!", show_alert=False)
    
    except Exception as e:
        await query.answer(f"❌ Error loading settings: {str(e)}", show_alert=True)

# ===========================
# BACKUP & RESTORE
# ===========================

@Bot.on_callback_query(filters.regex(r'^backup_config'))  # Added missing closing quote
async def backup_config(client: Bot, query: CallbackQuery):
    """Backup all settings"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    try:
        settings_keys = [
            'start_msg', 'start_pic', 'force_msg', 'force_channel',
            'caption', 'protect_content', 'auto_delete_time', 'auto_delete_msg',
            'auto_delete_success', 'disable_channel_button', 'user_reply',
            'stats_text', 'join_request'
        ]
        
        backup_data = {}
        for key in settings_keys:
            backup_data[key] = await safe_get_setting(key, 'Not Set')
        
        import json
        from datetime import datetime
        backup_json = json.dumps(backup_data, indent=2)
        
        await query.message.reply_document(
            document=backup_json.encode(),
            file_name=f"bot_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            caption="✅ <b>Configuration Backup</b>\n\nUse /setup restore to restore this backup."
        )
        await query.answer("✅ Backup created successfully!", show_alert=True)
    
    except Exception as e:
        await query.answer(f"❌ Backup failed: {str(e)}", show_alert=True)

@Bot.on_callback_query(filters.regex(r'^restore_config'))  # Added missing closing quote
async def restore_config(client: Bot, query: CallbackQuery):
    """Restore settings from backup"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    await query.message.edit_text(
        "📥 <b>Restore Configuration</b>\n\n"
        "Send me the backup JSON file to restore.\n\n"
        "Send <code>cancel</code> to abort.",
        reply_markup=back_keyboard("advanced")
    )
    await query.answer()
    
    response = await listen_for_input(client, query.message.chat.id, 60)
    
    if response is None or not response.document:
        await query.message.edit_text(
            "❌ <b>Cancelled or invalid file!</b>",
            reply_markup=back_keyboard("advanced")
        )
        return
    
    try:
        import json
        file_path = await response.download()
        with open(file_path, 'r') as f:
            backup_data = json.load(f)
        
        count = 0
        for key, value in backup_data.items():
            if value != 'Not Set':
                if await safe_update_setting(key, value):
                    count += 1
        
        await response.reply_text(
            f"✅ <b>Configuration restored successfully!</b>\n\n"
            f"<b>Restored {count}/{len(backup_data)} settings.</b>",
            reply_markup=back_keyboard("advanced")
        )
    except Exception as e:
        await response.reply_text(
            f"❌ <b>Restore failed:</b> {str(e)}",
            reply_markup=back_keyboard("advanced")
        )

# ===========================
# RESET CONFIRMATION
# ===========================

@Bot.on_callback_query(filters.regex(r'^restore_config'))  # Added missing closing quote
async def restore_config(client: Bot, query: CallbackQuery):
    """Restore settings from backup"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    await query.message.edit_text(
        "⚠️ <b>RESET ALL SETTINGS</b>\n\n"
        "Are you sure you want to reset ALL settings to default?\n\n"
        "<b>This action cannot be undone!</b>\n\n"
        "<i>Consider backing up first.</i>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💾 Backup First", callback_data="backup_config"),
            ],
            [
                InlineKeyboardButton("✅ Yes, Reset", callback_data="do_reset"),
                InlineKeyboardButton("❌ No, Cancel", callback_data="menu_advanced")
            ]
        ])
    )
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^do_reset'))  # Added missing closing quote
async def do_reset(client: Bot, query: CallbackQuery):
    """Actually perform the reset"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    try:
        from database.database import database
        if hasattr(database, 'settings_collection'):
            database.settings_collection.delete_many({})
        
        await query.message.edit_text(
            "✅ <b>All settings have been reset!</b>\n\n"
            "<i>Bot will now use environment variables or default values.</i>",
            reply_markup=back_keyboard("main")
        )
        await query.answer("✅ Reset completed!", show_alert=True)
    except Exception as e:
        await query.answer(f"❌ Reset failed: {str(e)}", show_alert=True)

# ===========================
# SHOW HELP
# ===========================

@Bot.on_callback_query(filters.regex(r'^show_help'))  # Added missing closing quote
async def show_help(client: Bot, query: CallbackQuery):
    """Show help menu"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ])
    )
    await query.answer()

# ===========================
# UTILITY HANDLERS
# ===========================

@Bot.on_callback_query(filters.regex(r'^close_panel'))  # Added missing closing quote
async def close_panel(client: Bot, query: CallbackQuery):
    """Close the setup panel"""
    if query.from_user.id not in [OWNER_ID] + ADMINS:
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return
    
    await query.message.delete()
    await query.answer("Setup panel closed!", show_alert=False)

@Bot.on_callback_query(filters.regex(r'^noop'))  # Added missing closing quote
async def noop_handler(client: Bot, query: CallbackQuery):
    """No operation - just answer the query"""
    await query.answer()
