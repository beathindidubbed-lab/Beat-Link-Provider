# plugins/setup_panel_new.py
# Beautiful working setup panel with all fixes

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import OWNER_ID, ADMINS
from database.database import get_setting, update_setting
import asyncio

# ===========================
# BEAUTIFUL MENUS
# ===========================

MAIN_MENU = """
╔════════════════════════════════╗
║   🎛️ <b>BOT CONTROL PANEL</b> 🎛️   ║
╚════════════════════════════════╝

<b>Welcome to the Setup Panel!</b>

Choose a category to configure:

🎨 <b>Appearance</b>
   Customize welcome messages & images

📢 <b>Channels</b>
   Configure DB & Force Subscribe channels

📝 <b>Messages</b>
   Set custom captions & replies

🔒 <b>Protection</b>
   Content security settings

⏱️ <b>Auto Delete</b>
   Automatic file cleanup

🔗 <b>URL Shortener</b>
   Link shortening configuration

<b>💡 Quick Commands:</b>
<code>/setchannel db</code> - Set DB channel
<code>/setchannel force</code> - Set force sub
<code>/viewchannels</code> - View channels

<b>Status:</b> ✅ All systems ready
"""

def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 Appearance", callback_data="setup_appearance"),
            InlineKeyboardButton("📢 Channels", callback_data="setup_channels")
        ],
        [
            InlineKeyboardButton("📝 Messages", callback_data="setup_messages"),
            InlineKeyboardButton("🔒 Protection", callback_data="setup_protection")
        ],
        [
            InlineKeyboardButton("⏱️ Auto Delete", callback_data="setup_autodelete"),
            InlineKeyboardButton("🔗 Shortener", callback_data="setup_shortener")
        ],
        [
            InlineKeyboardButton("👁️ View All", callback_data="setup_viewall"),
            InlineKeyboardButton("❓ Help", callback_data="setup_help")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="setup_main"),
            InlineKeyboardButton("❌ Close", callback_data="setup_close")
        ]
    ])

# ===========================
# MAIN COMMAND
# ===========================

@Bot.on_message(filters.command('setup') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def setup_panel(client: Bot, message: Message):
    """Main setup panel"""
    await message.reply_text(
        MAIN_MENU,
        reply_markup=main_keyboard(),
        quote=True
    )

# ===========================
# CALLBACK HANDLERS
# ===========================

@Bot.on_callback_query(filters.regex(r'^setup_main$'))
async def show_main_menu(client: Bot, query: CallbackQuery):
    """Show main menu"""
    await query.message.edit_text(
        MAIN_MENU,
        reply_markup=main_keyboard()
    )
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_channels$'))
async def setup_channels(client: Bot, query: CallbackQuery):
    """Channels configuration"""
    
    db_channel = get_setting('channel_id', 'Not Set')
    force_channel = get_setting('force_channel', '0')
    
    # Get channel names
    db_info = "Not configured"
    force_info = "Disabled"
    
    if db_channel != 'Not Set':
        try:
            chat = await client.get_chat(int(db_channel))
            db_info = f"{chat.title}\n<code>{db_channel}</code>"
        except:
            db_info = f"<code>{db_channel}</code>\n⚠️ Cannot access"
    
    if force_channel != '0':
        try:
            chat = await client.get_chat(int(force_channel))
            force_info = f"{chat.title}\n<code>{force_channel}</code>"
        except:
            force_info = f"<code>{force_channel}</code>\n⚠️ Cannot access"
    
    text = f"""
╔══════════════════════════════╗
║   📢 <b>CHANNEL SETTINGS</b>  📢   ║
╚══════════════════════════════╝

<b>📁 Database Channel:</b>
{db_info}

<b>📢 Force Subscribe:</b>
{force_info}

<b>🔧 How to Change:</b>
1. Run <code>/setchannel db</code> or <code>/setchannel force</code>
2. Forward ANY message from your channel
3. Bot auto-detects channel ID
4. Done! ✅

<b>💡 Easy Setup:</b>
Just forward a message - no need to find channel ID!
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📁 Set DB Channel", url=f"https://t.me/{client.username}?start=cmd_setchannel_db")
        ],
        [
            InlineKeyboardButton("📢 Set Force Sub", url=f"https://t.me/{client.username}?start=cmd_setchannel_force")
        ],
        [
            InlineKeyboardButton("👁️ View Details", callback_data="setup_viewchannels")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_appearance$'))
async def setup_appearance(client: Bot, query: CallbackQuery):
    """Appearance settings"""
    
    text = """
╔════════════════════════════╗
║   🎨 <b>APPEARANCE</b>  🎨   ║
╚════════════════════════════╝

Customize how your bot looks!

🖼️ <b>Start Picture</b>
Welcome image URL

💬 <b>Start Message</b>
Welcome text for users

📊 <b>Stats Format</b>
/stats command display

<b>✏️ Click below to edit:</b>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️ Start Picture", callback_data="edit_start_pic")
        ],
        [
            InlineKeyboardButton("💬 Start Message", callback_data="edit_start_msg")
        ],
        [
            InlineKeyboardButton("📊 Stats Format", callback_data="edit_stats_text")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_messages$'))
async def setup_messages(client: Bot, query: CallbackQuery):
    """Messages configuration"""
    
    text = """
╔══════════════════════════════╗
║   📝 <b>MESSAGE SETTINGS</b>  📝   ║
╚══════════════════════════════╝

Configure bot messages:

📄 <b>Custom Caption</b>
Add custom captions to files

💭 <b>User Reply</b>
Auto-reply to user messages

📢 <b>Force Sub Message</b>
Text when user not subscribed

<b>✏️ Click below to edit:</b>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 Custom Caption", callback_data="edit_caption")
        ],
        [
            InlineKeyboardButton("💭 User Reply", callback_data="edit_user_reply")
        ],
        [
            InlineKeyboardButton("📢 Force Sub Message", callback_data="edit_force_msg")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_protection$'))
async def setup_protection(client: Bot, query: CallbackQuery):
    """Protection settings"""
    
    protect = get_setting('protect_content', 'False')
    button = get_setting('disable_channel_button', 'False')
    
    text = f"""
╔════════════════════════════╗
║   🔒 <b>PROTECTION</b>  🔒   ║
╚════════════════════════════╝

Security settings:

🔒 <b>Protect Content</b>
Status: {'✅ Enabled' if protect == 'True' else '❌ Disabled'}
Prevents forwarding files

🔘 <b>Channel Button</b>
Status: {'🙈 Hidden' if button == 'True' else '👁️ Visible'}
Share button on posts

<b>⚙️ Click to toggle:</b>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"🔒 Protect: {'ON ✅' if protect == 'True' else 'OFF ❌'}",
                callback_data="toggle_protect"
            )
        ],
        [
            InlineKeyboardButton(
                f"🔘 Button: {'Hidden 🙈' if button == 'True' else 'Visible 👁️'}",
                callback_data="toggle_button"
            )
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_autodelete$'))
async def setup_autodelete(client: Bot, query: CallbackQuery):
    """Auto delete settings"""
    
    time = get_setting('auto_delete_time', '0')
    mins = int(time) // 60 if time != '0' else 0
    
    text = f"""
╔══════════════════════════════╗
║   ⏱️ <b>AUTO DELETE</b>  ⏱️   ║
╚══════════════════════════════╝

Automatic file deletion:

⏱️ <b>Delete Timer</b>
Current: {time}s ({mins} minutes)
Status: {'✅ Enabled' if int(time) > 0 else '❌ Disabled'}

💬 <b>Warning Message</b>
Shown before deletion

✅ <b>Success Message</b>
Shown after deletion

<b>✏️ Click below to edit:</b>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱️ Set Timer", callback_data="edit_autodel_time")
        ],
        [
            InlineKeyboardButton("💬 Warning Text", callback_data="edit_autodel_msg"),
            InlineKeyboardButton("✅ Success Text", callback_data="edit_autodel_success")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_shortener$'))
async def setup_shortener(client: Bot, query: CallbackQuery):
    """URL shortener settings"""
    
    enabled = get_setting('shortener_enabled', 'False')
    
    text = f"""
╔══════════════════════════════╗
║   🔗 <b>URL SHORTENER</b>  🔗   ║
╚══════════════════════════════╝

Link shortening service:

🔄 <b>Status</b>
{'✅ Enabled' if enabled == 'True' else '❌ Disabled'}

🔑 <b>API Key</b>
Your shortener API

🌐 <b>Site URL</b>
Shortener website

<b>Supported:</b> Linkvertise, Shorte.st, GPLinks

<b>⚙️ Click to configure:</b>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"🔄 {'Disable' if enabled == 'True' else 'Enable'}",
                callback_data="toggle_shortener"
            )
        ],
        [
            InlineKeyboardButton("🔑 Set API Key", callback_data="edit_shortener_api"),
            InlineKeyboardButton("🌐 Set Site", callback_data="edit_shortener_site")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_viewall$'))
async def view_all_settings(client: Bot, query: CallbackQuery):
    """View all settings"""
    
    # Get all settings
    settings = {
        'start_msg': get_setting('start_msg', 'Default'),
        'start_pic': get_setting('start_pic', 'None'),
        'channel_id': get_setting('channel_id', 'Not Set'),
        'force_channel': get_setting('force_channel', '0'),
        'caption': get_setting('caption', 'None'),
        'protect': get_setting('protect_content', 'False'),
        'autodel': get_setting('auto_delete_time', '0'),
        'shortener': get_setting('shortener_enabled', 'False')
    }
    
    def short(text, length=30):
        text = str(text)
        return text[:length] + '...' if len(text) > length else text
    
    text = f"""
╔═══════════════════════════════╗
║   📊 <b>ALL SETTINGS</b>  📊   ║
╚═══════════════════════════════╝

🎨 <b>Appearance</b>
• Start Message: {short(settings['start_msg'])}
• Start Picture: {short(settings['start_pic'])}

📢 <b>Channels</b>
• Database: <code>{settings['channel_id']}</code>
• Force Sub: <code>{settings['force_channel']}</code>

📝 <b>Messages</b>
• Caption: {short(settings['caption'])}

🔒 <b>Protection</b>
• Protect Content: {settings['protect']}

⏱️ <b>Auto Delete</b>
• Timer: {settings['autodel']}s

🔗 <b>Shortener</b>
• Status: {settings['shortener']}

<i>Use the buttons below to edit</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="setup_viewall")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer("Settings loaded!", show_alert=False)

@Bot.on_callback_query(filters.regex(r'^setup_help$'))
async def setup_help(client: Bot, query: CallbackQuery):
    """Show help"""
    
    text = """
╔════════════════════════════╗
║   ❓ <b>HELP</b>  ❓   ║
╚════════════════════════════╝

<b>🎯 Quick Commands:</b>

<b>Channels:</b>
• <code>/setchannel db</code>
• <code>/setchannel force</code>
• <code>/viewchannels</code>

<b>Setup:</b>
• <code>/setup</code> - This panel
• <code>/verify</code> - Verify setup

<b>Testing:</b>
• <code>/ping</code> - Test bot
• <code>/test</code> - Run tests

<b>💡 Tips:</b>

1️⃣ <b>Set channels easily:</b>
   Just forward a message from your channel!

2️⃣ <b>Click commands to run:</b>
   Tap any command above

3️⃣ <b>Use buttons:</b>
   All settings accessible via buttons

<b>Need more help?</b>
Check logs or contact @CodeXBotzSupport
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Back", callback_data="setup_main")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^setup_close$'))
async def close_setup(client: Bot, query: CallbackQuery):
    """Close setup panel"""
    await query.message.delete()
    await query.answer("Panel closed!", show_alert=False)

# ===========================
# TOGGLE HANDLERS
# ===========================

@Bot.on_callback_query(filters.regex(r'^toggle_protect$'))
async def toggle_protect(client: Bot, query: CallbackQuery):
    """Toggle content protection"""
    current = get_setting('protect_content', 'False')
    new_value = 'False' if current == 'True' else 'True'
    update_setting('protect_content', new_value)
    
    await query.answer(
        f"✅ Protect Content {'Enabled' if new_value == 'True' else 'Disabled'}!",
        show_alert=True
    )
    
    # Refresh the protection menu
    await setup_protection(client, query)

@Bot.on_callback_query(filters.regex(r'^toggle_button$'))
async def toggle_button(client: Bot, query: CallbackQuery):
    """Toggle channel button"""
    current = get_setting('disable_channel_button', 'False')
    new_value = 'False' if current == 'True' else 'True'
    update_setting('disable_channel_button', new_value)
    
    await query.answer(
        f"✅ Channel Button {'Hidden' if new_value == 'True' else 'Visible'}!",
        show_alert=True
    )
    
    # Refresh the protection menu
    await setup_protection(client, query)

@Bot.on_callback_query(filters.regex(r'^toggle_shortener$'))
async def toggle_shortener(client: Bot, query: CallbackQuery):
    """Toggle URL shortener"""
    current = get_setting('shortener_enabled', 'False')
    new_value = 'False' if current == 'True' else 'True'
    update_setting('shortener_enabled', new_value)
    
    await query.answer(
        f"✅ URL Shortener {'Enabled' if new_value == 'True' else 'Disabled'}!",
        show_alert=True
    )
    
    # Refresh the shortener menu
    await setup_shortener(client, query)

# ===========================
# EDIT HANDLERS (Simple version)
# ===========================

@Bot.on_callback_query(filters.regex(r'^edit_'))
async def handle_edits(client: Bot, query: CallbackQuery):
    """Handle edit callbacks"""
    
    edit_type = query.data.replace('edit_', '')
    
    messages = {
        'start_pic': "Send new start picture URL or 'none' to remove:",
        'start_msg': "Send new start message (use {first}, {last}, etc):",
        'stats_text': "Send new stats format (use {uptime}):",
        'caption': "Send new caption or 'none' (use {filename}, {previouscaption}):",
        'user_reply': "Send new user reply or 'none':",
        'force_msg': "Send new force subscribe message:",
        'autodel_time': "Send time in seconds (0 to disable):",
        'autodel_msg': "Send warning message (use {time}):",
        'autodel_success': "Send success message:",
        'shortener_api': "Send your shortener API key:",
        'shortener_site': "Send shortener site URL:"
    }
    
    if edit_type in messages:
        await query.message.reply_text(
            f"✏️ <b>Edit {edit_type.replace('_', ' ').title()}</b>\n\n"
            f"{messages[edit_type]}\n\n"
            f"Send <code>cancel</code> to abort",
            quote=True
        )
        
        await query.answer(f"Waiting for your input...", show_alert=False)
    else:
        await query.answer("This feature is coming soon!", show_alert=True)
