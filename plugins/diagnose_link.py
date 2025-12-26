# plugins/diagnose_link.py
# Diagnostic tool to find link issues

from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import OWNER_ID, ADMINS
from helper_func import decode, encode

@Bot.on_message(filters.command('diagnose') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def diagnose_link(client: Bot, message: Message):
    """Diagnose why links aren't working"""
    
    msg = await message.reply_text("🔍 <b>Running Diagnostics...</b>", quote=True)
    
    results = []
    results.append("╔═══════════════════════════════╗")
    results.append("║   🔬 <b>LINK DIAGNOSTICS</b>  🔬   ║")
    results.append("╚═══════════════════════════════╝\n")
    
    # Test 1: Check if db_channel exists
    results.append("<b>1️⃣ Database Channel Check:</b>")
    if hasattr(client, 'db_channel') and client.db_channel:
        results.append(f"✅ DB Channel: {client.db_channel.id}")
        results.append(f"✅ Channel Name: {client.db_channel.title}\n")
        db_ok = True
    else:
        results.append("❌ DB Channel not configured!\n")
        db_ok = False
    
    # Test 2: Check encoding/decoding
    results.append("<b>2️⃣ Encode/Decode Test:</b>")
    try:
        test_string = "get-1234567890"
        encoded = await encode(test_string)
        decoded = await decode(encoded)
        
        if test_string == decoded:
            results.append(f"✅ Encoding works: {encoded[:20]}...")
            results.append(f"✅ Decoding works: {decoded}\n")
            encode_ok = True
        else:
            results.append(f"❌ Decode mismatch!")
            results.append(f"   Original: {test_string}")
            results.append(f"   Decoded: {decoded}\n")
            encode_ok = False
    except Exception as e:
        results.append(f"❌ Encode/Decode error: {e}\n")
        encode_ok = False
    
    # Test 3: Generate a test link
    results.append("<b>3️⃣ Link Generation Test:</b>")
    if db_ok:
        try:
            test_msg_id = 1
            converted_id = test_msg_id * abs(client.db_channel.id)
            link_string = f"get-{converted_id}"
            encoded_link = await encode(link_string)
            full_link = f"https://t.me/{client.username}?start={encoded_link}"
            
            results.append(f"✅ Test Message ID: {test_msg_id}")
            results.append(f"✅ Converted: {converted_id}")
            results.append(f"✅ Encoded: {encoded_link[:30]}...")
            results.append(f"✅ Link: {full_link[:50]}...\n")
            link_ok = True
        except Exception as e:
            results.append(f"❌ Link generation error: {e}\n")
            link_ok = False
    else:
        results.append("⏭️ Skipped (no DB channel)\n")
        link_ok = False
    
    # Test 4: Check handlers
    results.append("<b>4️⃣ Handler Check:</b>")
    try:
        import plugins.start as start_module
        
        # Check if subscribed filter exists
        from helper_func import subscribed
        results.append("✅ Subscribed filter found")
        
        # Check if start command exists
        results.append("✅ Start handlers loaded\n")
        handler_ok = True
    except Exception as e:
        results.append(f"❌ Handler error: {e}\n")
        handler_ok = False
    
    # Test 5: Simulate link click
    results.append("<b>5️⃣ Link Processing Test:</b>")
    if encode_ok and db_ok:
        try:
            # Simulate what happens when user clicks link
            test_param = encoded_link
            simulated_text = f"/start {test_param}"
            
            # Try to decode it
            decoded_param = await decode(test_param)
            parts = decoded_param.split("-")
            
            results.append(f"✅ Simulated: /start {test_param[:20]}...")
            results.append(f"✅ Decoded: {decoded_param}")
            results.append(f"✅ Parts: {len(parts)} parts")
            
            if len(parts) == 2:
                try:
                    msg_id = int(int(parts[1]) / abs(client.db_channel.id))
                    results.append(f"✅ Calculated Message ID: {msg_id}\n")
                    process_ok = True
                except Exception as e:
                    results.append(f"❌ ID calculation error: {e}\n")
                    process_ok = False
            else:
                results.append(f"❌ Invalid format (expected 2 parts)\n")
                process_ok = False
        except Exception as e:
            results.append(f"❌ Processing error: {e}\n")
            process_ok = False
    else:
        results.append("⏭️ Skipped (previous tests failed)\n")
        process_ok = False
    
    # Summary
    results.append("<b>📊 Summary:</b>")
    results.append(f"DB Channel: {'✅' if db_ok else '❌'}")
    results.append(f"Encoding: {'✅' if encode_ok else '❌'}")
    results.append(f"Link Gen: {'✅' if link_ok else '❌'}")
    results.append(f"Handlers: {'✅' if handler_ok else '❌'}")
    results.append(f"Processing: {'✅' if process_ok else '❌'}\n")
    
    if all([db_ok, encode_ok, link_ok, handler_ok, process_ok]):
        results.append("<b>✅ All tests passed!</b>")
        results.append("Links should be working.\n")
        results.append("<b>🧪 Next Step:</b>")
        results.append("Send me: /testfile")
    else:
        results.append("<b>❌ Some tests failed!</b>")
        results.append("Check the errors above.\n")
        results.append("<b>🔧 Common Fixes:</b>")
        if not db_ok:
            results.append("• Run: /setchannel db")
        if not encode_ok:
            results.append("• Check helper_func.py")
        if not handler_ok:
            results.append("• Check plugins/start.py")
    
    await msg.edit_text("\n".join(results))


@Bot.on_message(filters.command('testfile') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def test_file_link(client: Bot, message: Message):
    """Create a real test link"""
    
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply_text("❌ DB Channel not configured!", quote=True)
        return
    
    msg = await message.reply_text(
        "📝 <b>Test File Link</b>\n\n"
        "Forward a message from your database channel, and I'll create a test link.",
        quote=True
    )
    
    try:
        # Wait for forwarded message
        response = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
        
        if not response.forward_from_chat or response.forward_from_chat.id != client.db_channel.id:
            await msg.edit_text("❌ That message is not from the database channel!")
            return
        
        # Get message ID
        msg_id = response.forward_from_message_id
        
        # Generate link
        converted_id = msg_id * abs(client.db_channel.id)
        link_string = f"get-{converted_id}"
        encoded = await encode(link_string)
        link = f"https://t.me/{client.username}?start={encoded}"
        
        result = f"""
✅ <b>Test Link Created!</b>

<b>📋 Details:</b>
• Message ID: <code>{msg_id}</code>
• Channel ID: <code>{client.db_channel.id}</code>
• Converted: <code>{converted_id}</code>
• Encoded: <code>{encoded[:30]}...</code>

<b>🔗 Test Link:</b>
{link}

<b>🧪 Test Instructions:</b>
1. Click the link above
2. Bot should send you the file
3. If it shows welcome instead, there's a handler issue

<b>📊 What Should Happen:</b>
• Link parameter: <code>{encoded[:20]}...</code>
• Decode to: <code>{link_string}</code>
• Calculate: <code>{converted_id} / {abs(client.db_channel.id)} = {msg_id}</code>
• Fetch message {msg_id} from channel
• Send to you

<b>If it doesn't work:</b>
Send me the error you see or screenshot
"""
        
        await msg.edit_text(result)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


@Bot.on_message(filters.command('checkstart') & filters.private & filters.user([OWNER_ID] + ADMINS))
async def check_start_handler(client: Bot, message: Message):
    """Check what's in start.py"""
    
    try:
        with open('plugins/start.py', 'r') as f:
            content = f.read()
        
        # Check for key indicators
        checks = []
        checks.append("🔍 <b>Checking start.py:</b>\n")
        
        # Check 1: Has parameter handling
        if "len(text) > 7" in content or "len(message.text) > 7" in content:
            checks.append("✅ Has parameter detection")
        else:
            checks.append("❌ Missing parameter detection")
        
        # Check 2: Has base64 decode
        if "decode(base64_string)" in content or "await decode" in content:
            checks.append("✅ Has decode function")
        else:
            checks.append("❌ Missing decode function")
        
        # Check 3: Has get_messages
        if "get_messages" in content:
            checks.append("✅ Has get_messages call")
        else:
            checks.append("❌ Missing get_messages call")
        
        # Check 4: Two start handlers
        start_count = content.count("@Bot.on_message(filters.command('start')")
        checks.append(f"\n📊 Found {start_count} /start handlers")
        
        if start_count == 2:
            checks.append("✅ Has subscribed and non-subscribed handlers")
        else:
            checks.append(f"⚠️ Expected 2 handlers, found {start_count}")
        
        # Check 5: Handler order
        subscribed_pos = content.find("subscribed")
        not_subscribed_pos = content.find("filters.command('start') & filters.private)")
        
        if subscribed_pos > 0 and not_subscribed_pos > subscribed_pos:
            checks.append("✅ Handler order correct")
        else:
            checks.append("⚠️ Handler order might be wrong")
        
        # Show file size
        checks.append(f"\n📄 File size: {len(content)} characters")
        checks.append(f"📄 Lines: {len(content.splitlines())} lines")
        
        # Check for common issues
        checks.append("\n🔍 <b>Common Issues:</b>")
        if "return" not in content:
            checks.append("⚠️ Missing return statements")
        
        if content.count("await send_welcome_message") > 0:
            checks.append("✅ Uses send_welcome_message function")
        elif "START_MSG" in content:
            checks.append("✅ Has START_MSG reference")
        else:
            checks.append("⚠️ Missing welcome message")
        
        await message.reply_text("\n".join(checks), quote=True)
        
    except Exception as e:
        await message.reply_text(f"❌ Error reading start.py: {e}", quote=True)


@Bot.on_message(filters.regex(r'^/start .+') & filters.private)
async def debug_start_params(client: Bot, message: Message):
    """Debug any /start with parameter"""
    
    # Only for owner/admins and only if not handled by other handlers
    if message.from_user.id not in [OWNER_ID] + ADMINS:
        return
    
    # This runs AFTER normal handlers, so only catches unhandled cases
    await asyncio.sleep(2)  # Wait for normal handlers
    
    text = message.text
    param = text.split(" ", 1)[1] if len(text.split()) > 1 else "none"
    
    debug_msg = f"""
🔍 <b>Debug: /start Parameter Detected</b>

<b>Raw Text:</b> <code>{text[:100]}</code>
<b>Parameter:</b> <code>{param[:50]}</code>
<b>Param Length:</b> {len(param)}

<b>⚠️ This means the normal handler didn't catch it!</b>

<b>Possible Issues:</b>
• Handler not registered
• Filter not matching
• Error in handler code

<b>Check console logs for errors!</b>
"""
    
    await message.reply_text(debug_msg, quote=True)
