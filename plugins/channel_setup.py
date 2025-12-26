# plugins/channel_setup.py
# New feature to set channels by forwarding messages

from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import OWNER_ID, ADMINS
from database.database import update_setting
import asyncio

@Bot.on_message(filters.command('setchannel') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def set_channel_command(client: Bot, message: Message):
    """
    Set database or force subscribe channel by forwarding a message
    Usage: /setchannel db OR /setchannel force
    """
    
    # Check command argument
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2 or args[1].lower() not in ['db', 'force', 'database', 'forcesub']:
        await message.reply_text(
            "📋 <b>Set Channel Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/setchannel db</code> - Set database channel\n"
            "• <code>/setchannel force</code> - Set force subscribe channel\n\n"
            "<b>After running command:</b>\n"
            "Forward any message from your channel to bot\n\n"
            "<b>Example:</b>\n"
            "1. Send <code>/setchannel db</code>\n"
            "2. Forward a message from your channel\n"
            "3. Bot will detect channel ID automatically\n"
            "4. Channel will be set instantly! ✅",
            quote=True
        )
        return
    
    channel_type = args[1].lower()
    is_db = channel_type in ['db', 'database']
    
    msg = await message.reply_text(
        f"📢 <b>Setting {'Database' if is_db else 'Force Subscribe'} Channel</b>\n\n"
        "✅ <b>Step 1: Forward a message</b>\n"
        "Forward ANY message from your channel to me\n\n"
        "⏱️ <b>Waiting 60 seconds...</b>\n\n"
        "Send <code>cancel</code> to abort",
        quote=True
    )
    
    try:
        # Wait for user to forward a message
        response = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
        
        # Check if it's from a channel
        if not response.forward_from_chat:
            await msg.edit_text(
                "❌ <b>Error!</b>\n\n"
                "That message is not forwarded from a channel.\n\n"
                "<b>Please:</b>\n"
                "1. Go to your channel\n"
                "2. Forward ANY message from it\n"
                "3. Send it to me\n\n"
                "Try again with <code>/setchannel {'db' if is_db else 'force'}</code>"
            )
            return
        
        # Get channel info
        channel = response.forward_from_chat
        channel_id = channel.id
        channel_title = channel.title
        channel_username = f"@{channel.username}" if channel.username else "Private Channel"
        
        # Verify bot has access
        try:
            await msg.edit_text(
                f"🔍 <b>Verifying channel access...</b>\n\n"
                f"Channel: {channel_title}\n"
                f"ID: <code>{channel_id}</code>"
            )
            
            # Try to get full chat info
            chat = await client.get_chat(channel_id)
            
            # Check bot membership
            me = await client.get_me()
            member = await client.get_chat_member(channel_id, me.id)
            
            if member.status not in ["administrator", "creator"]:
                await msg.edit_text(
                    f"⚠️ <b>Bot is not admin!</b>\n\n"
                    f"<b>Channel:</b> {channel_title}\n"
                    f"<b>ID:</b> <code>{channel_id}</code>\n"
                    f"<b>Bot Status:</b> {member.status}\n\n"
                    f"<b>Required:</b>\n"
                    f"1. Add bot as admin to channel\n"
                    f"2. Give permissions: Post, Edit, Delete\n"
                    f"3. Try this command again\n\n"
                    f"<i>You can still set it, but it may not work until bot is admin.</i>\n\n"
                    f"Set anyway? Reply <code>yes</code> or <code>no</code>"
                )
                
                confirm = await client.listen(message.chat.id, timeout=30)
                if confirm.text.lower() != 'yes':
                    await msg.edit_text("❌ <b>Cancelled!</b>")
                    return
            
            # Test permissions for DB channel
            if is_db:
                try:
                    test_msg = await client.send_message(channel_id, "✅ Bot connection test")
                    await asyncio.sleep(1)
                    await test_msg.delete()
                    permissions_ok = True
                except Exception as e:
                    permissions_ok = False
                    perm_error = str(e)
            else:
                # For force sub, just check if we can create invite link
                try:
                    link = await client.export_chat_invite_link(channel_id)
                    permissions_ok = True
                except Exception as e:
                    permissions_ok = False
                    perm_error = str(e)
            
            # Save to database
            if is_db:
                update_setting('channel_id', str(channel_id))
                # Also update the client's db_channel
                client.db_channel = chat
            else:
                update_setting('force_channel', str(channel_id))
                # Update invite link
                try:
                    link = await client.export_chat_invite_link(channel_id)
                    client.invitelink = link
                except:
                    pass
            
            # Success message
            success_text = f"""
✅ <b>{'Database' if is_db else 'Force Subscribe'} Channel Set Successfully!</b>

<b>📋 Channel Details:</b>
├ <b>Name:</b> {channel_title}
├ <b>Username:</b> {channel_username}
├ <b>ID:</b> <code>{channel_id}</code>
└ <b>Type:</b> {chat.type}

<b>🤖 Bot Status:</b>
├ <b>Membership:</b> {member.status}
"""
            
            if is_db:
                success_text += f"└ <b>Permissions:</b> {'✅ Working' if permissions_ok else '❌ Need admin rights'}\n\n"
                if permissions_ok:
                    success_text += "<b>✅ Bot can post, edit, and delete messages!</b>\n"
                else:
                    success_text += f"<b>⚠️ Error:</b> <code>{perm_error}</code>\n\n"
                    success_text += "<b>Fix:</b> Make bot admin with Post/Edit/Delete permissions\n"
            else:
                success_text += f"└ <b>Invite Link:</b> {'✅ Created' if permissions_ok else '❌ Need admin rights'}\n\n"
                if permissions_ok:
                    success_text += "<b>✅ Force subscribe is ready!</b>\n"
                else:
                    success_text += f"<b>⚠️ Error:</b> <code>{perm_error}</code>\n\n"
                    success_text += "<b>Fix:</b> Make bot admin with 'Invite Users' permission\n"
            
            success_text += f"\n<b>💾 Configuration Saved!</b>\n"
            success_text += f"<i>Restart bot to apply changes fully.</i>"
            
            await msg.edit_text(success_text)
            
        except Exception as e:
            await msg.edit_text(
                f"❌ <b>Error verifying channel!</b>\n\n"
                f"<b>Channel:</b> {channel_title}\n"
                f"<b>ID:</b> <code>{channel_id}</code>\n"
                f"<b>Error:</b> <code>{str(e)}</code>\n\n"
                f"<b>Possible Issues:</b>\n"
                f"1. Bot is not in the channel\n"
                f"2. Bot is not admin\n"
                f"3. Channel is private and bot has no access\n\n"
                f"<b>Fix:</b>\n"
                f"1. Add bot to channel: @{me.username}\n"
                f"2. Make it admin\n"
                f"3. Try again"
            )
    
    except asyncio.TimeoutError:
        await msg.edit_text(
            "⏱️ <b>Timeout!</b>\n\n"
            "You didn't forward a message in time.\n\n"
            f"Try again with <code>/setchannel {'db' if is_db else 'force'}</code>"
        )
    
    except Exception as e:
        await msg.edit_text(
            f"❌ <b>Error:</b> <code>{str(e)}</code>\n\n"
            "Please try again or contact support."
        )


@Bot.on_message(filters.command('viewchannels') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def view_channels(client: Bot, message: Message):
    """View currently configured channels"""
    
    from database.database import get_setting
    
    db_channel = get_setting('channel_id', 'Not Set')
    force_channel = get_setting('force_channel', '0')
    
    # Try to get channel names
    db_name = "Not Set"
    force_name = "Disabled"
    
    if db_channel != 'Not Set':
        try:
            chat = await client.get_chat(int(db_channel))
            db_name = f"{chat.title} (@{chat.username if chat.username else 'Private'})"
        except:
            db_name = f"ID: {db_channel} (Cannot access)"
    
    if force_channel != '0':
        try:
            chat = await client.get_chat(int(force_channel))
            force_name = f"{chat.title} (@{chat.username if chat.username else 'Private'})"
        except:
            force_name = f"ID: {force_channel} (Cannot access)"
    
    info = f"""
╔═══════════════════════════════╗
║  📢 <b>CONFIGURED CHANNELS</b>  📢  ║
╚═══════════════════════════════╝

<b>📁 Database Channel:</b>
├ <b>ID:</b> <code>{db_channel}</code>
└ <b>Name:</b> {db_name}

<b>📢 Force Subscribe Channel:</b>
├ <b>ID:</b> <code>{force_channel}</code>
└ <b>Name:</b> {force_name}

<b>🛠️ Commands:</b>
• <code>/setchannel db</code> - Change DB channel
• <code>/setchannel force</code> - Change force sub channel
• <code>/viewchannels</code> - View this info

<b>💡 Tip:</b>
Forward any message from your channel after running /setchannel
Bot will auto-detect the channel ID!
"""
    
    await message.reply_text(info, quote=True)
