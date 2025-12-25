#(©)CodeXBotz

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
import config
from helper_func import subscribed, decode, get_messages, delete_file, shorten_url
from database.database import add_user, del_user, full_userbase, present_user

# Help messages for different user types
USER_HELP_TEXT = """
╔══════════════════════════════╗
║  📚 <b>USER COMMANDS</b>  📚  ║
╚══════════════════════════════╝

<b>Available Commands:</b>

🚀 <b>/start</b> - Start the bot
📚 <b>/help</b> - Show this help message

<b>How to Use:</b>

1️⃣ Click on any file link shared by admins
2️⃣ The bot will send you the file
3️⃣ If auto-delete is enabled, save the file quickly!
4️⃣ Use the "Get File Again" button if needed

<b>Features:</b>
✅ Fast file delivery
✅ Protected content (if enabled)
✅ Auto-delete for privacy
✅ Re-send capability

<b>Need Help?</b>
Contact the bot owner for support.

<i>Powered by CodeXBotz</i>
"""

ADMIN_HELP_TEXT = """
╔══════════════════════════════╗
║  🛠️ <b>ADMIN COMMANDS</b>  🛠️  ║
╚══════════════════════════════╝

<b>📁 File Management:</b>
• <b>/batch</b> - Create batch link (multiple files)
• <b>/genlink</b> - Generate single file link
• <b>/custom_batch</b> - Custom batch with range

<b>📊 Bot Management:</b>
• <b>/users</b> - Get total user count
• <b>/broadcast</b> - Broadcast message to all users
• <b>/stats</b> - Check bot uptime and statistics

<b>⚙️ Configuration:</b>
• <b>/setup</b> - Open setup panel
• <b>/setup help</b> - View all setup commands
• <b>/setup view</b> - View all current settings

<b>📝 Quick Setup Commands:</b>
• <code>/setup start_msg</code> - Edit welcome message
• <code>/setup force_channel</code> - Set force sub channel
• <code>/setup caption</code> - Set custom caption
• <code>/setup autodel_time</code> - Set auto-delete timer
• <code>/setup protect</code> - Toggle content protection
• <code>/setup shortener</code> - Toggle URL shortener

<b>🎯 File Sharing Workflow:</b>
1️⃣ Forward files to bot privately
2️⃣ Bot automatically creates shareable links
3️⃣ Share links with users
4️⃣ Users click links to get files

<b>💡 Pro Tips:</b>
• Use <code>/batch</code> for multiple files
• Enable auto-delete for sensitive content
• Use custom captions for branding
• Enable URL shortener for cleaner links

<b>🔗 Batch Link Format:</b>
• Single: <code>?start=get-123456</code>
• Batch: <code>?start=get-123456-123460</code>

<i>For detailed setup guide, use /setup help</i>
"""

@Bot.on_message(filters.command('help') & filters.private)
async def help_command(client: Client, message: Message):
    """Show help based on user role"""
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id in [config.OWNER_ID] + config.ADMINS:
        help_text = ADMIN_HELP_TEXT
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Setup Panel", callback_data="open_setup"),
                InlineKeyboardButton("📊 View Stats", callback_data="view_stats")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close_help")
            ]
        ])
    else:
        help_text = USER_HELP_TEXT
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔒 Close", callback_data="close_help")
            ]
        ])
    
    await message.reply_text(
        help_text,
        reply_markup=keyboard,
        quote=True
    )

@Bot.on_callback_query(filters.regex(r'^open_setup$'))
async def open_setup_callback(client: Bot, query):
    """Open setup panel from help"""
    if query.from_user.id not in [config.OWNER_ID] + config.ADMINS:
        await query.answer("❌ Only admins can access setup!", show_alert=True)
        return
    
    from plugins.setup_command import MAIN_MENU_TEXT, main_menu_keyboard
    await query.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=main_menu_keyboard()
    )
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^view_stats$'))
async def view_stats_callback(client: Bot, query):
    """View bot stats from help"""
    if query.from_user.id not in [config.OWNER_ID] + config.ADMINS:
        await query.answer("❌ Only admins can view stats!", show_alert=True)
        return
    
    from datetime import datetime
    from helper_func import get_readable_time
    
    users = await full_userbase()
    now = datetime.now()
    delta = now - client.uptime
    time = get_readable_time(delta.seconds)
    
    BOT_STATS_TEXT = config.get_bot_stats_text()
    stats_text = BOT_STATS_TEXT.format(uptime=time)
    stats_text += f"\n\n<b>Total Users:</b> <code>{len(users)}</code>"
    
    await query.message.edit_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="back_to_help")]
        ])
    )
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^back_to_help$'))
async def back_to_help_callback(client: Bot, query):
    """Go back to help from stats"""
    user_id = query.from_user.id
    
    if user_id in [config.OWNER_ID] + config.ADMINS:
        help_text = ADMIN_HELP_TEXT
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Setup Panel", callback_data="open_setup"),
                InlineKeyboardButton("📊 View Stats", callback_data="view_stats")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close_help")
            ]
        ])
    else:
        help_text = USER_HELP_TEXT
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 Close", callback_data="close_help")]
        ])
    
    await query.message.edit_text(help_text, reply_markup=keyboard)
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^close_help$'))
async def close_help_callback(client: Bot, query):
    """Close help message"""
    await query.message.delete()
    await query.answer("Help closed!")

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        track_msgs = []
        
        # Get dynamic config values
        CUSTOM_CAPTION = config.get_custom_caption()
        DISABLE_CHANNEL_BUTTON = config.get_disable_channel_button()
        PROTECT_CONTENT = config.get_protect_content()
        AUTO_DELETE_TIME = config.get_auto_delete_time()
        AUTO_DELETE_MSG = config.get_auto_delete_msg()

        for msg in messages:
            # Handle custom caption with blockquote support
            if bool(CUSTOM_CAPTION) and bool(msg.document):
                prev_caption = "" if not msg.caption else msg.caption.html
                filename = msg.document.file_name
                caption = CUSTOM_CAPTION.format(
                    previouscaption=prev_caption,
                    filename=filename
                )
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                try:
                    copied_msg_for_deletion = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    if copied_msg_for_deletion:
                        track_msgs.append(copied_msg_for_deletion)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    copied_msg_for_deletion = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    if copied_msg_for_deletion:
                        track_msgs.append(copied_msg_for_deletion)
                except Exception as e:
                    print(f"Error copying message: {e}")
                    pass
            else:
                try:
                    await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    await asyncio.sleep(0.5)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                except:
                    pass

        if track_msgs:
            # Create original link for re-send button
            original_link = f"https://t.me/{client.username}?start={base64_string}"
            
            delete_data = await client.send_message(
                chat_id=message.from_user.id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            # Schedule the file deletion task
            asyncio.create_task(delete_file(track_msgs, client, delete_data, original_link))

        return
    else:
        # Get dynamic config values
        START_MSG = config.get_start_msg()
        START_PIC = config.get_start_pic()
        
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😊 About Me", callback_data="about"),
                InlineKeyboardButton("📚 Help", callback_data="show_user_help")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
        
        if START_PIC:
            await message.reply_photo(
                photo=START_PIC,
                caption=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                quote=True
            )
        else:
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                quote=True
            )
        return

@Bot.on_callback_query(filters.regex(r'^show_user_help$'))
async def show_user_help(client: Bot, query):
    """Show help from start menu"""
    await query.message.edit_text(
        USER_HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")],
            [InlineKeyboardButton("🔒 Close", callback_data="close")]
        ])
    )
    await query.answer()

@Bot.on_callback_query(filters.regex(r'^back_to_start$'))
async def back_to_start(client: Bot, query):
    """Go back to start message"""
    START_MSG = config.get_start_msg()
    
    await query.message.edit_text(
        START_MSG.format(
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😊 About Me", callback_data="about"),
                InlineKeyboardButton("📚 Help", callback_data="show_user_help")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
    )
    await query.answer()

WAIT_MSG = "<b>Processing ...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    JOIN_REQUEST_ENABLE = config.get_join_request()
    FORCE_SUB_CHANNEL = config.get_force_sub_channel()
    FORCE_MSG = config.get_force_msg()

    if bool(JOIN_REQUEST_ENABLE):
        invite = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNEL,
            creates_join_request=True
        )
        ButtonUrl = invite.invite_link
    else:
        ButtonUrl = client.invitelink

    buttons = [
        [
            InlineKeyboardButton("Join Channel", url=ButtonUrl)
        ]
    ]

    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user([config.OWNER_ID] + config.ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user([config.OWNER_ID] + config.ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        newline = "\n"
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
