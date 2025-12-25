# plugins/simple_start.py
# Replace your start.py with this temporarily to test

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
import config

# Simple start command that ALWAYS works
@Bot.on_message(filters.command('start') & filters.private)
async def simple_start(client: Bot, message: Message):
    """Simplified start command for testing"""
    
    # Log that we received the command
    print(f"✅ /start received from {message.from_user.id} - {message.from_user.first_name}")
    
    try:
        # Get user info
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        
        # Basic welcome message
        welcome_text = f"""
👋 <b>Hello {first_name}!</b>

✅ Bot is working!

<b>Your Info:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Username:</b> {f"@{user.username}" if user.username else "None"}
• <b>Name:</b> {first_name}

<b>💡 Test Commands:</b>
• <code>/ping</code> - Test connection
• <code>/test</code> - Run tests
• <code>/help</code> - Get help

<b>🤖 Bot Info:</b>
• <b>Username:</b> @{client.username}
• <b>Status:</b> ✅ Online

<i>Bot is configured and ready!</i>
"""
        
        # Simple keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Bot Working!", callback_data="about"),
                InlineKeyboardButton("📚 Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
        
        # Send response
        await message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            quote=True
        )
        
        print(f"✅ Response sent successfully to {user_id}")
        
    except Exception as e:
        print(f"❌ Error in start command: {e}")
        import traceback
        traceback.print_exc()
        
        # Send error message to user
        try:
            await message.reply_text(
                f"❌ <b>Error occurred:</b>\n\n<code>{str(e)}</code>\n\n"
                "Please contact admin.",
                quote=True
            )
        except:
            pass


# Callback handlers
@Bot.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Bot, query):
    """About button handler"""
    await query.answer()
    
    about_text = f"""
╔═══════════════════════════╗
║  ℹ️ <b>ABOUT THIS BOT</b>  ℹ️  ║
╚═══════════════════════════╝

<b>🤖 Bot Information:</b>
• <b>Username:</b> @{client.username}
• <b>Version:</b> 2.0
• <b>Framework:</b> Pyrogram
• <b>Language:</b> Python 3

<b>📋 Features:</b>
✅ File Sharing
✅ Batch Links
✅ Custom Captions
✅ Auto Delete
✅ Force Subscribe
✅ Protected Content

<b>👨‍💻 Developer:</b>
<a href="https://t.me/CodeXBotz">CodeXBotz</a>

<b>💬 Support:</b>
<a href="https://t.me/CodeXBotzSupport">Support Group</a>
"""
    
    await query.message.edit_text(
        about_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
        ]),
        disable_web_page_preview=True
    )


@Bot.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Bot, query):
    """Help button handler"""
    await query.answer()
    
    # Check if admin
    if query.from_user.id in [config.OWNER_ID] + config.ADMINS:
        help_text = """
╔════════════════════════════╗
║  🛠️ <b>ADMIN COMMANDS</b>  🛠️  ║
╚════════════════════════════╝

<b>📁 File Management:</b>
• <code>/batch</code> - Create batch link
• <code>/genlink</code> - Single file link
• <code>/custom_batch</code> - Custom range

<b>📊 Bot Management:</b>
• <code>/users</code> - Total users
• <code>/broadcast</code> - Broadcast message
• <code>/stats</code> - Bot statistics

<b>⚙️ Configuration:</b>
• <code>/setup</code> - Setup panel
• <code>/verify</code> - Verify setup

<b>🔧 Testing:</b>
• <code>/ping</code> - Test connection
• <code>/test</code> - Run tests
• <code>/debug</code> - Debug info
"""
    else:
        help_text = """
╔════════════════════════════╗
║  📚 <b>USER COMMANDS</b>  📚  ║
╚════════════════════════════╝

<b>Available Commands:</b>
• <code>/start</code> - Start bot
• <code>/ping</code> - Test connection
• <code>/help</code> - This help

<b>How to Use:</b>
1. Click file links shared by admin
2. Bot will send you files
3. Save files before auto-delete

<b>Need Help?</b>
Contact bot admin for support.
"""
    
    await query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
        ])
    )


@Bot.on_callback_query(filters.regex("^back_start$"))
async def back_start_callback(client: Bot, query):
    """Back to start button"""
    await query.answer()
    
    user = query.from_user
    
    welcome_text = f"""
👋 <b>Hello {user.first_name}!</b>

✅ Bot is working!

<b>Your Info:</b>
• <b>User ID:</b> <code>{user.id}</code>
• <b>Username:</b> {f"@{user.username}" if user.username else "None"}
• <b>Name:</b> {user.first_name}

<b>💡 Test Commands:</b>
• <code>/ping</code> - Test connection
• <code>/test</code> - Run tests
• <code>/help</code> - Get help

<b>🤖 Bot Info:</b>
• <b>Username:</b> @{client.username}
• <b>Status:</b> ✅ Online

<i>Bot is configured and ready!</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Bot Working!", callback_data="about"),
            InlineKeyboardButton("📚 Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(
        welcome_text,
        reply_markup=keyboard
    )


@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Bot, query):
    """Close button handler"""
    await query.message.delete()
    await query.answer("Closed!", show_alert=False)


# Log all incoming messages for debugging
@Bot.on_message(filters.private)
async def log_incoming(client: Bot, message: Message):
    """Log all messages (runs after other handlers)"""
    if message.text:
        print(f"📨 Message from {message.from_user.id}: {message.text[:50]}")
    continue_propagation = True  # Let other handlers process
