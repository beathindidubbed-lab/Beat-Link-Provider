#(©)Codexbotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, ADMINS
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    if data == "about":
        await query.message.edit_text(
            text=f"<b>○ Creator : <a href='tg://user?id={OWNER_ID}'>This Person</a>\n○ Language : <code>Python3</code>\n○ Library : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio {__version__}</a>\n○ Source Code : <a href='https://github.com/CodeXBotz/File-Sharing-Bot'>Click here</a>\n○ Channel : @CodeXBotz\n○ Support Group : @CodeXBotzSupport</b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔒 Close", callback_data="close")]
            ])
        )
    
    elif data == "help":
        # Check if user is admin
        user_id = query.from_user.id
        
        if user_id in [OWNER_ID] + ADMINS:
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
            text=help_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ])
        )
    
    elif data == "back_to_start":
        # Get user info
        user = query.from_user
        
        from config import START_MSG, START_PIC
        
        welcome_text = START_MSG.format(
            first=user.first_name,
            last=user.last_name if user.last_name else "",
            username=f"@{user.username}" if user.username else "None",
            mention=user.mention,
            id=user.id
        )
        
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😊 About Me", callback_data="about"),
                InlineKeyboardButton("📚 Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])
        
        if START_PIC:
            try:
                await query.message.delete()
                await client.send_photo(
                    chat_id=query.message.chat.id,
                    photo=START_PIC,
                    caption=welcome_text,
                    reply_markup=reply_markup
                )
            except:
                await query.message.edit_text(
                    text=welcome_text,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
        else:
            await query.message.edit_text(
                text=welcome_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
