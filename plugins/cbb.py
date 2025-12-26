#(©)Codexbotz
# Fixed version with back button in about and improved UI

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, ADMINS, START_MSG, START_PIC
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    user = query.from_user
    
    if data == "about":
        about_text = f"""
╔═══════════════════════════════╗
║   ℹ️ <b>ABOUT BOT</b>  ℹ️   ║
╚═══════════════════════════════╝

<b>🤖 Bot Information:</b>
• <b>Name:</b> {client.me.first_name}
• <b>Username:</b> @{client.username}
• <b>Language:</b> Python 3
• <b>Framework:</b> Pyrogram {__version__}

<b>👨‍💻 Developer:</b>
• <a href='tg://user?id={OWNER_ID}'>Owner</a>
• <a href='https://t.me/CodeXBotz'>CodeXBotz Channel</a>
• <a href='https://t.me/CodeXBotzSupport'>Support Group</a>

<b>⚡ Features:</b>
✅ File Sharing System
✅ Batch File Links
✅ Custom Captions
✅ Auto Delete Files
✅ Force Subscribe
✅ Protected Content
✅ URL Shortener
✅ Beautiful UI

<b>📜 License:</b>
GNU General Public License v3.0

<b>🔗 Source Code:</b>
<a href='https://github.com/CodeXBotz/File-Sharing-Bot'>GitHub Repository</a>
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_start")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
        
        await query.message.edit_text(
            text=about_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        await query.answer()
    
    elif data == "help":
        # Check if user is admin
        user_id = user.id
        
        if user_id in [OWNER_ID] + ADMINS:
            help_text = """
╔═══════════════════════════════╗
║   🛠️ <b>ADMIN COMMANDS</b>  🛠️   ║
╚═══════════════════════════════╝

<b>📁 File Management:</b>
• /batch - Create batch link for multiple files
• /genlink - Create link for single file
• /custom_batch - Custom range batch link

<b>📊 Bot Management:</b>
• /users - View total user count
• /broadcast - Broadcast message to all users
• /stats - View bot statistics & uptime

<b>⚙️ Configuration:</b>
• /setup - Open setup panel
• /setchannel db - Set database channel
• /setchannel force - Set force subscribe channel
• /viewchannels - View configured channels

<b>🔧 Testing & Debug:</b>
• /ping - Test bot connection
• /test - Run system tests
• /debug - Show debug information
• /verify - Verify bot setup

<b>💡 Pro Tips:</b>
1. Use /setchannel and forward a message from your channel
2. Bot auto-detects channel ID - no manual entry needed!
3. Use /setup for beautiful configuration panel
4. Run /verify to check if everything is working

<b>🆘 Need Help?</b>
Join @CodeXBotzSupport for assistance
"""
        else:
            help_text = """
╔═══════════════════════════════╗
║   📚 <b>USER COMMANDS</b>  📚   ║
╚═══════════════════════════════╝

<b>Available Commands:</b>
• /start - Start the bot & see welcome
• /ping - Test bot connection
• /help - Show this help message

<b>🎯 How to Use Bot:</b>

<b>Step 1:</b> Get a file link from admin
<b>Step 2:</b> Click the link or send /start CODE
<b>Step 3:</b> Bot will send you the file(s)
<b>Step 4:</b> Save files before auto-delete (if enabled)

<b>📝 Important Notes:</b>
• Join required channels to access files
• Some files may auto-delete after time limit
• Forward button may be disabled on protected files
• Bot may require you to join a channel first

<b>⚠️ Troubleshooting:</b>
• If bot doesn't respond: /start
• If file doesn't send: Check if you joined channels
• If link expired: Contact person who shared it

<b>🆘 Need Help?</b>
Contact the bot admin for support

<b>💬 Feedback:</b>
Report issues or suggestions to admin
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_start")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
        
        await query.message.edit_text(
            text=help_text,
            reply_markup=keyboard
        )
        await query.answer()
    
    elif data == "back_to_start":
        # Recreate start message
        welcome_text = START_MSG.format(
            first=user.first_name,
            last=user.last_name if user.last_name else "",
            username=f"@{user.username}" if user.username else "None",
            mention=user.mention,
            id=user.id
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😊 About", callback_data="about"),
                InlineKeyboardButton("📚 Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
        
        # If there's a start picture, try to recreate with photo
        if START_PIC:
            try:
                # Delete current message
                await query.message.delete()
                # Send new photo message
                await client.send_photo(
                    chat_id=query.message.chat.id,
                    photo=START_PIC,
                    caption=welcome_text,
                    reply_markup=keyboard
                )
            except Exception as e:
                # If photo fails, just edit text
                await query.message.edit_text(
                    text=welcome_text,
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
        else:
            await query.message.edit_text(
                text=welcome_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        
        await query.answer()
    
    elif data == "close":
        await query.message.delete()
        try:
            # Try to delete the command message too
            await query.message.reply_to_message.delete()
        except:
            pass
        await query.answer("Closed!", show_alert=False)
