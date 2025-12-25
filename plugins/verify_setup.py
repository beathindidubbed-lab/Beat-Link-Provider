# plugins/verify_setup.py
# Add this as a new file to diagnose and fix channel issues

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChannelPrivate, ChannelInvalid, PeerIdInvalid, UserNotParticipant
from bot import Bot
from config import OWNER_ID, ADMINS, CHANNEL_ID, FORCE_SUB_CHANNEL

@Bot.on_message(filters.command('verify') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def verify_setup(client: Bot, message: Message):
    """
    Verify bot setup and permissions
    Usage: /verify
    """
    
    msg = await message.reply_text("🔍 <b>Verifying Bot Setup...</b>")
    
    results = []
    results.append("╔═══════════════════════════════╗")
    results.append("║  🔍 <b>BOT SETUP VERIFICATION</b>  🔍  ║")
    results.append("╚═══════════════════════════════╝\n")
    
    # 1. Check Bot Info
    try:
        bot_info = await client.get_me()
        results.append("✅ <b>Bot Information:</b>")
        results.append(f"├ Username: @{bot_info.username}")
        results.append(f"├ Bot ID: <code>{bot_info.id}</code>")
        results.append(f"└ Name: {bot_info.first_name}\n")
    except Exception as e:
        results.append(f"❌ <b>Bot Info Error:</b> {str(e)}\n")
    
    # 2. Check Database Channel
    results.append("📁 <b>Database Channel Check:</b>")
    try:
        db_channel = await client.get_chat(CHANNEL_ID)
        results.append(f"├ Channel ID: <code>{CHANNEL_ID}</code>")
        results.append(f"├ Channel Title: {db_channel.title}")
        results.append(f"├ Channel Type: {db_channel.type}")
        
        # Check bot permissions
        try:
            bot_member = await client.get_chat_member(CHANNEL_ID, bot_info.id)
            results.append(f"├ Bot Status: {bot_member.status}")
            
            if bot_member.status in ["administrator", "creator"]:
                perms = bot_member.privileges
                if perms:
                    results.append("├ Permissions:")
                    results.append(f"│  ├ Post Messages: {'✅' if perms.can_post_messages else '❌'}")
                    results.append(f"│  ├ Edit Messages: {'✅' if perms.can_edit_messages else '❌'}")
                    results.append(f"│  ├ Delete Messages: {'✅' if perms.can_delete_messages else '❌'}")
                    results.append(f"│  └ Manage Chat: {'✅' if perms.can_manage_chat else '❌'}")
                else:
                    results.append("│  └ ⚠️ No specific permissions (might be using default)")
                
                # Test sending message
                try:
                    test_msg = await client.send_message(CHANNEL_ID, "🔍 Verification Test Message")
                    await test_msg.delete()
                    results.append("└ ✅ <b>Test Message: SUCCESS</b>\n")
                except Exception as e:
                    results.append(f"└ ❌ <b>Test Message Failed:</b> {str(e)}\n")
            else:
                results.append(f"└ ❌ <b>Bot is not admin! Current status: {bot_member.status}</b>\n")
                
        except Exception as e:
            results.append(f"└ ❌ <b>Permission Check Failed:</b> {str(e)}\n")
            
    except ChannelPrivate:
        results.append(f"❌ Channel is private and bot is not a member")
        results.append(f"└ Please add bot to channel: <code>{CHANNEL_ID}</code>\n")
    except ChannelInvalid:
        results.append(f"❌ Invalid channel ID: <code>{CHANNEL_ID}</code>")
        results.append("└ Check your CHANNEL_ID in config\n")
    except PeerIdInvalid:
        results.append(f"❌ Peer ID Invalid: <code>{CHANNEL_ID}</code>")
        results.append("└ Make sure the channel ID is correct\n")
    except Exception as e:
        results.append(f"❌ <b>Database Channel Error:</b> {str(e)}\n")
    
    # 3. Check Force Subscribe Channel
    if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL != 0:
        results.append("📢 <b>Force Subscribe Channel Check:</b>")
        try:
            force_channel = await client.get_chat(FORCE_SUB_CHANNEL)
            results.append(f"├ Channel ID: <code>{FORCE_SUB_CHANNEL}</code>")
            results.append(f"├ Channel Title: {force_channel.title}")
            results.append(f"├ Channel Type: {force_channel.type}")
            
            # Check bot permissions
            try:
                bot_member = await client.get_chat_member(FORCE_SUB_CHANNEL, bot_info.id)
                results.append(f"├ Bot Status: {bot_member.status}")
                
                if bot_member.status in ["administrator", "creator"]:
                    perms = bot_member.privileges
                    if perms:
                        results.append("├ Permissions:")
                        results.append(f"│  ├ Invite Users: {'✅' if perms.can_invite_users else '❌'}")
                        results.append(f"│  └ Manage Chat: {'✅' if perms.can_manage_chat else '❌'}")
                    
                    # Test invite link
                    try:
                        invite_link = await client.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        results.append(f"└ ✅ <b>Invite Link: Generated</b>\n")
                    except Exception as e:
                        results.append(f"└ ❌ <b>Invite Link Failed:</b> {str(e)}\n")
                else:
                    results.append(f"└ ❌ <b>Bot is not admin! Current status: {bot_member.status}</b>\n")
                    
            except Exception as e:
                results.append(f"└ ❌ <b>Permission Check Failed:</b> {str(e)}\n")
                
        except ChannelPrivate:
            results.append(f"❌ Channel is private and bot is not a member")
            results.append(f"└ Please add bot to channel: <code>{FORCE_SUB_CHANNEL}</code>\n")
        except ChannelInvalid:
            results.append(f"❌ Invalid channel ID: <code>{FORCE_SUB_CHANNEL}</code>")
            results.append("└ Check your FORCE_SUB_CHANNEL in config\n")
        except PeerIdInvalid:
            results.append(f"❌ Peer ID Invalid: <code>{FORCE_SUB_CHANNEL}</code>")
            results.append("└ Make sure the channel ID is correct and includes -100 prefix\n")
        except Exception as e:
            results.append(f"❌ <b>Force Subscribe Channel Error:</b> {str(e)}\n")
    else:
        results.append("📢 <b>Force Subscribe:</b> ❌ Disabled\n")
    
    # 4. Configuration Summary
    results.append("⚙️ <b>Configuration Summary:</b>")
    results.append(f"├ Owner ID: <code>{OWNER_ID}</code>")
    results.append(f"├ Database Channel: <code>{CHANNEL_ID}</code>")
    results.append(f"├ Force Sub Channel: <code>{FORCE_SUB_CHANNEL if FORCE_SUB_CHANNEL else 'Disabled'}</code>")
    results.append(f"└ Admins Count: <code>{len(ADMINS)}</code>\n")
    
    # 5. Recommendations
    results.append("💡 <b>Recommendations:</b>")
    
    # Check if all is good
    all_good = True
    try:
        await client.get_chat(CHANNEL_ID)
        bot_member = await client.get_chat_member(CHANNEL_ID, bot_info.id)
        if bot_member.status not in ["administrator", "creator"]:
            all_good = False
            results.append("❌ Make bot admin in Database Channel")
    except:
        all_good = False
        results.append("❌ Fix Database Channel configuration")
    
    if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL != 0:
        try:
            await client.get_chat(FORCE_SUB_CHANNEL)
            bot_member = await client.get_chat_member(FORCE_SUB_CHANNEL, bot_info.id)
            if bot_member.status not in ["administrator", "creator"]:
                all_good = False
                results.append("❌ Make bot admin in Force Subscribe Channel")
        except:
            all_good = False
            results.append("❌ Fix Force Subscribe Channel configuration")
    
    if all_good:
        results.append("✅ All configurations are correct!")
        results.append("✅ Bot is ready to use!")
    else:
        results.append("\n<b>🔧 Quick Fix Steps:</b>")
        results.append("1. Open your channel as admin")
        results.append("2. Add bot to channel (if not added)")
        results.append("3. Make bot admin with these permissions:")
        results.append("   • Post Messages")
        results.append("   • Edit Messages")
        results.append("   • Delete Messages")
        results.append("   • Invite Users (for force sub)")
        results.append("4. Run <code>/verify</code> again")
    
    final_text = "\n".join(results)
    
    await msg.edit_text(final_text)


@Bot.on_message(filters.command('fixchannel') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def fix_channel(client: Bot, message: Message):
    """
    Interactive channel fix guide
    Usage: /fixchannel
    """
    
    guide = """
╔════════════════════════════════╗
║  🔧 <b>CHANNEL FIX GUIDE</b>  🔧  ║
╚════════════════════════════════╝

<b>📁 Database Channel Setup:</b>

1️⃣ <b>Get Channel ID:</b>
   • Forward any message from your channel to @userinfobot
   • Copy the Channel ID (e.g., -1001234567890)
   • Set this as CHANNEL_ID in your config

2️⃣ <b>Add Bot to Channel:</b>
   • Go to your channel
   • Click "Subscribers" or channel info
   • Click "Add Admin" or "Add Members"
   • Search for your bot username
   • Add the bot

3️⃣ <b>Make Bot Admin:</b>
   • In channel, go to Administrators
   • Click on your bot
   • Enable these permissions:
     ✅ Post Messages
     ✅ Edit Messages
     ✅ Delete Messages
     ✅ Add Subscribers (optional)

4️⃣ <b>Verify Setup:</b>
   • Send <code>/verify</code> to check configuration
   • Bot should show ✅ for all checks

<b>📢 Force Subscribe Channel Setup:</b>

1️⃣ Follow same steps as Database Channel
2️⃣ Additionally enable:
   ✅ Invite Users via Link
3️⃣ Set channel ID as FORCE_SUB_CHANNEL

<b>⚠️ Common Issues:</b>

❌ <b>"Peer ID Invalid"</b>
   → Channel ID is wrong or missing -100 prefix
   → Get correct ID from @userinfobot

❌ <b>"Channel is Private"</b>
   → Bot is not added to channel
   → Add bot as member first

❌ <b>"Permission Denied"</b>
   → Bot is not admin
   → Make bot admin with proper permissions

❌ <b>"Bot can't Export Invite Link"</b>
   → Bot needs "Invite Users" permission
   → Enable this in admin settings

<b>🔍 Debug Commands:</b>
• <code>/verify</code> - Check setup status
• <code>/fixchannel</code> - Show this guide

<b>💡 Pro Tip:</b>
Create a private channel specifically for file storage (Database Channel) and a public channel for force subscribe if needed.

<b>Need more help?</b>
Join @CodeXBotzSupport for assistance!
"""
    
    await message.reply_text(guide, quote=True)


@Bot.on_message(filters.command('getchannelid') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def get_channel_id(client: Bot, message: Message):
    """
    Get channel ID by forwarding a message
    Usage: Forward any message from your channel, then reply with /getchannelid
    """
    
    if not message.reply_to_message:
        await message.reply_text(
            "❌ <b>Usage:</b>\n\n"
            "1. Forward any message from your channel\n"
            "2. Reply to that forwarded message with <code>/getchannelid</code>",
            quote=True
        )
        return
    
    replied_msg = message.reply_to_message
    
    if replied_msg.forward_from_chat:
        chat = replied_msg.forward_from_chat
        
        info = f"""
✅ <b>Channel Information:</b>

<b>Channel Name:</b> {chat.title}
<b>Channel ID:</b> <code>{chat.id}</code>
<b>Channel Type:</b> {chat.type}
<b>Channel Username:</b> {'@' + chat.username if chat.username else 'Private Channel'}

<b>💡 To use this channel:</b>

<b>For Database Channel:</b>
Set <code>CHANNEL_ID={chat.id}</code> in your config

<b>For Force Subscribe:</b>
Set <code>FORCE_SUB_CHANNEL={chat.id}</code> in your config

<b>Next Steps:</b>
1. Add bot to this channel
2. Make bot admin with proper permissions
3. Run <code>/verify</code> to test
"""
        await message.reply_text(info, quote=True)
    else:
        await message.reply_text(
            "❌ <b>Error:</b>\n\n"
            "This message is not forwarded from a channel.\n"
            "Please forward a message from your channel and try again.",
            quote=True
        )


@Bot.on_message(filters.command('testdb') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def test_database(client: Bot, message: Message):
    """
    Test database connection
    Usage: /testdb
    """
    
    msg = await message.reply_text("🔍 Testing database connection...")
    
    try:
        from database.database import present_user, add_user, full_userbase
        
        # Test reading
        test_user_id = message.from_user.id
        is_present = await present_user(test_user_id)
        
        # Test writing
        if not is_present:
            await add_user(test_user_id)
        
        # Test listing
        users = await full_userbase()
        
        result = f"""
✅ <b>Database Test Successful!</b>

<b>Connection:</b> ✅ Working
<b>Read Operation:</b> ✅ Success
<b>Write Operation:</b> ✅ Success
<b>Total Users:</b> <code>{len(users)}</code>

<b>Database Type:</b> {type(database).__name__}
<b>Your User Status:</b> {'Already registered' if is_present else 'Newly registered'}
"""
        await msg.edit_text(result)
        
    except Exception as e:
        await msg.edit_text(
            f"❌ <b>Database Test Failed!</b>\n\n"
            f"<b>Error:</b> <code>{str(e)}</code>\n\n"
            f"<b>Solution:</b>\n"
            f"1. Check DATABASE_URL in config\n"
            f"2. Verify database is accessible\n"
            f"3. Check database credentials"
        )
