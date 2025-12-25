# plugins/test_handlers.py
# Add this file to test if bot is receiving messages

from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import OWNER_ID, ADMINS

@Bot.on_message(filters.command('ping') & filters.private)
async def ping_handler(client: Bot, message: Message):
    """Test if bot is responding - works for everyone"""
    await message.reply_text(
        "🏓 <b>Pong!</b>\n\n"
        "✅ Bot is online and responding!\n\n"
        f"<b>Your ID:</b> <code>{message.from_user.id}</code>\n"
        f"<b>Your Name:</b> {message.from_user.first_name}\n"
        f"<b>Bot Username:</b> @{client.username}",
        quote=True
    )
    print(f"✅ Received /ping from {message.from_user.id}")


@Bot.on_message(filters.command('test') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def test_handler(client: Bot, message: Message):
    """Admin test command"""
    from datetime import datetime
    
    test_info = f"""
╔═══════════════════════════╗
║  🧪 <b>BOT TEST RESULTS</b>  🧪  ║
╚═══════════════════════════╝

<b>✅ Bot Status:</b> Online
<b>✅ Message Handler:</b> Working
<b>✅ Bot Username:</b> @{client.username}
<b>✅ Bot ID:</b> <code>{(await client.get_me()).id}</code>

<b>📊 Your Info:</b>
├ <b>User ID:</b> <code>{message.from_user.id}</code>
├ <b>Username:</b> {f"@{message.from_user.username}" if message.from_user.username else "None"}
├ <b>Name:</b> {message.from_user.first_name}
└ <b>Admin Status:</b> {"✅ Yes" if message.from_user.id in [OWNER_ID] + ADMINS else "❌ No"}

<b>🕐 Current Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>💡 Available Commands:</b>
• <code>/ping</code> - Test connection
• <code>/test</code> - This test
• <code>/debug</code> - Debug info
• <code>/start</code> - Start command
"""
    
    await message.reply_text(test_info, quote=True)
    print(f"✅ Received /test from {message.from_user.id}")


@Bot.on_message(filters.command('debug') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def debug_handler(client: Bot, message: Message):
    """Show debug information"""
    import config
    
    debug_info = f"""
╔════════════════════════════╗
║  🔍 <b>DEBUG INFORMATION</b>  🔍  ║
╚════════════════════════════╝

<b>📱 Bot Configuration:</b>
├ <b>Username:</b> @{client.username}
├ <b>Bot ID:</b> <code>{(await client.get_me()).id}</code>
└ <b>API ID:</b> <code>{config.APP_ID}</code>

<b>📁 Channels:</b>
├ <b>DB Channel ID:</b> <code>{config.CHANNEL_ID}</code>
├ <b>Force Sub ID:</b> <code>{config.FORCE_SUB_CHANNEL if config.FORCE_SUB_CHANNEL else 'Disabled'}</code>
└ <b>Invite Link:</b> {hasattr(client, 'invitelink') and client.invitelink is not None}

<b>🗄️ Database:</b>
├ <b>DB Type:</b> {config.DB_TYPE}
├ <b>DB Name:</b> {config.DB_NAME}
└ <b>DB Connected:</b> {"✅ Yes" if config.DB_URI else "❌ No"}

<b>👥 Admins:</b>
├ <b>Owner ID:</b> <code>{config.OWNER_ID}</code>
└ <b>Total Admins:</b> <code>{len(config.ADMINS)}</code>

<b>⚙️ Features:</b>
├ <b>Protect Content:</b> {config.PROTECT_CONTENT}
├ <b>Auto Delete:</b> {f"{config.AUTO_DELETE_TIME}s" if config.AUTO_DELETE_TIME else "Disabled"}
└ <b>Custom Caption:</b> {"Enabled" if config.CUSTOM_CAPTION else "Disabled"}

<b>🔍 Current Message:</b>
├ <b>Chat Type:</b> {message.chat.type}
├ <b>Message ID:</b> <code>{message.id}</code>
└ <b>Timestamp:</b> {message.date}
"""
    
    await message.reply_text(debug_info, quote=True)
    print(f"✅ Received /debug from {message.from_user.id}")


@Bot.on_message(filters.private)
async def log_all_messages(client: Bot, message: Message):
    """Log all incoming messages for debugging"""
    user = message.from_user
    msg_type = "command" if message.text and message.text.startswith('/') else "message"
    msg_text = message.text[:50] if message.text else "non-text message"
    
    print(f"📨 Received {msg_type} from {user.id} ({user.first_name}): {msg_text}")
    
    # Don't reply here, let other handlers process it
    # This is just for logging


@Bot.on_message(filters.command('forceerror'))
async def force_error(client: Bot, message: Message):
    """Force an error to test error handling"""
    if message.from_user.id not in [OWNER_ID] + ADMINS:
        return
    
    await message.reply_text("⚠️ Forcing an error for testing...")
    raise Exception("Test error - this is intentional!")


# Test if force subscribe is working
@Bot.on_message(filters.command('testforce') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def test_force_sub(client: Bot, message: Message):
    """Test force subscribe functionality"""
    import config
    
    if not config.FORCE_SUB_CHANNEL or config.FORCE_SUB_CHANNEL == 0:
        await message.reply_text(
            "❌ <b>Force Subscribe is Disabled</b>\n\n"
            "Set FORCE_SUB_CHANNEL to enable it.",
            quote=True
        )
        return
    
    try:
        # Try to get channel
        channel = await client.get_chat(config.FORCE_SUB_CHANNEL)
        
        # Try to get member status
        try:
            member = await client.get_chat_member(config.FORCE_SUB_CHANNEL, message.from_user.id)
            status = member.status
        except:
            status = "Not a member"
        
        # Try to get invite link
        try:
            if hasattr(client, 'invitelink') and client.invitelink:
                invite = client.invitelink
            else:
                invite = await client.export_chat_invite_link(config.FORCE_SUB_CHANNEL)
        except Exception as e:
            invite = f"Error: {e}"
        
        result = f"""
╔════════════════════════════════╗
║  📢 <b>FORCE SUB TEST</b>  📢  ║
╚════════════════════════════════╝

<b>✅ Channel Found!</b>

<b>📋 Channel Info:</b>
├ <b>Name:</b> {channel.title}
├ <b>ID:</b> <code>{config.FORCE_SUB_CHANNEL}</code>
├ <b>Type:</b> {channel.type}
└ <b>Username:</b> {f"@{channel.username}" if channel.username else "Private"}

<b>👤 Your Status:</b>
└ {status}

<b>🔗 Invite Link:</b>
<code>{invite[:100]}</code>

<b>💡 Test Result:</b>
{"✅ Force Subscribe is configured correctly!" if "http" in str(invite) else "⚠️ Bot cannot create invite links - needs 'Invite Users' permission"}
"""
        
        await message.reply_text(result, quote=True)
        
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Force Subscribe Test Failed!</b>\n\n"
            f"<b>Error:</b> <code>{str(e)}</code>\n\n"
            f"<b>Channel ID:</b> <code>{config.FORCE_SUB_CHANNEL}</code>\n\n"
            f"<b>Solutions:</b>\n"
            f"1. Check if channel ID is correct\n"
            f"2. Make sure bot is in the channel\n"
            f"3. Make bot admin with invite permission\n"
            f"4. Or set FORCE_SUB_CHANNEL=0 to disable",
            quote=True
        )
