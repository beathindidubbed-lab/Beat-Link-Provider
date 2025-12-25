#(©)Codexbotz
# plugins/custom_batch.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import OWNER_ID, ADMINS
from helper_func import encode, shorten_url

@Bot.on_message(filters.private & filters.user([OWNER_ID] + ADMINS) & filters.command('custom_batch'))
async def custom_batch(client: Client, message: Message):
    """
    Advanced batch link generator with custom range selection
    Supports: individual IDs, ranges, and mixed formats
    """
    
    help_msg = """
╔════════════════════════════════╗
║  📦 <b>CUSTOM BATCH GENERATOR</b>  📦  ║
╚════════════════════════════════╝

<b>Create custom batch links with flexible ranges!</b>

<b>📝 Format Options:</b>

<b>1️⃣ Single Range:</b>
<code>123-130</code>
Creates link for messages 123 to 130

<b>2️⃣ Multiple Ranges:</b>
<code>123-130, 145-150</code>
Multiple separate ranges

<b>3️⃣ Individual IDs:</b>
<code>123, 125, 130</code>
Specific message IDs only

<b>4️⃣ Mixed Format:</b>
<code>123-130, 145, 150-155</code>
Combines ranges and individual IDs

<b>⚠️ Important Notes:</b>
• Use commas to separate ranges/IDs
• No spaces in range (123-130 not 123 - 130)
• Maximum 200 messages per link
• All IDs must be from DB channel

<b>💡 Examples:</b>
• <code>100-150</code>
• <code>100-110, 120-130</code>
• <code>100, 105, 110-115</code>

<b>Send your range/IDs below:</b>
<i>Type <code>cancel</code> to abort</i>
"""
    
    msg = await message.reply_text(help_msg, quote=True)
    
    try:
        # Wait for user response
        response = await client.listen(message.chat.id, timeout=300)
        
        if response.text.lower() in ['cancel', '/cancel']:
            await msg.edit_text("❌ <b>Cancelled!</b>")
            return
        
        # Parse the input
        try:
            message_ids = parse_custom_range(response.text)
        except ValueError as e:
            await response.reply_text(
                f"❌ <b>Invalid Format!</b>\n\n{str(e)}\n\nPlease try again with <code>/custom_batch</code>",
                quote=True
            )
            return
        
        # Validate message count
        if len(message_ids) > 200:
            await response.reply_text(
                f"❌ <b>Too many messages!</b>\n\n"
                f"You requested <b>{len(message_ids)}</b> messages.\n"
                f"Maximum allowed: <b>200</b> messages per link.\n\n"
                f"Please reduce the range and try again.",
                quote=True
            )
            return
        
        if len(message_ids) == 0:
            await response.reply_text(
                "❌ <b>No valid message IDs found!</b>\n\n"
                "Please check your input format and try again.",
                quote=True
            )
            return
        
        # Generate batch link
        processing = await response.reply_text(
            f"⏳ <b>Generating batch link...</b>\n\n"
            f"<b>Total Messages:</b> <code>{len(message_ids)}</code>",
            quote=True
        )
        
        # Convert IDs to database channel format
        first_id = min(message_ids) * abs(client.db_channel.id)
        last_id = max(message_ids) * abs(client.db_channel.id)
        
        # Create batch string
        string = f"get-{first_id}-{last_id}"
        base64_string = await encode(string)
        
        # Generate link
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        # Try to shorten URL if enabled
        shortened_link = await shorten_url(link)
        
        # Create response
        link_text = f"""
✅ <b>Custom Batch Link Generated!</b>

<b>📊 Batch Details:</b>
├ <b>Total Messages:</b> <code>{len(message_ids)}</code>
├ <b>Start ID:</b> <code>{min(message_ids)}</code>
├ <b>End ID:</b> <code>{max(message_ids)}</code>
└ <b>Range:</b> <code>{response.text}</code>

<b>🔗 Your Batch Link:</b>
<code>{shortened_link if shortened_link != link else link}</code>

<b>💡 Share this link to give access to all {len(message_ids)} files!</b>
"""
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Share Link", url=f'https://telegram.me/share/url?url={shortened_link}')],
            [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{base64_string}")]
        ])
        
        await processing.edit_text(
            link_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Error occurred:</b>\n\n<code>{str(e)}</code>\n\n"
            "Please try again or contact support.",
            quote=True
        )

def parse_custom_range(text: str) -> list:
    """
    Parse custom range input into list of message IDs
    Supports: 123-130, 145, 150-155
    """
    message_ids = []
    
    # Split by comma
    parts = [p.strip() for p in text.split(',')]
    
    for part in parts:
        if '-' in part:
            # Range format: 123-130
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                
                if start > end:
                    raise ValueError(f"Invalid range: {start}-{end}. Start must be less than end.")
                
                # Add all IDs in range
                message_ids.extend(range(start, end + 1))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid number in range: {part}")
                raise e
        else:
            # Single ID
            try:
                msg_id = int(part.strip())
                message_ids.append(msg_id)
            except ValueError:
                raise ValueError(f"Invalid message ID: {part}")
    
    # Remove duplicates and sort
    message_ids = sorted(list(set(message_ids)))
    
    return message_ids

@Bot.on_callback_query(filters.regex(r'^copy_'))
async def copy_link_callback(client: Bot, query):
    """Handle copy link callback"""
    base64_string = query.data.split('_', 1)[1]
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    await query.answer(
        f"Link copied!\n{link}",
        show_alert=True
    )

# Additional command: /range_help for detailed examples
@Bot.on_message(filters.private & filters.user([OWNER_ID] + ADMINS) & filters.command('range_help'))
async def range_help(client: Client, message: Message):
    """Show detailed examples for custom batch"""
    
    examples = """
╔═══════════════════════════════════╗
║  📖 <b>CUSTOM BATCH - EXAMPLES</b>  📖  ║
╚═══════════════════════════════════╝

<b>🎯 Real-World Examples:</b>

<b>Example 1: Simple Range</b>
<b>Input:</b> <code>100-150</code>
<b>Result:</b> Messages 100 to 150 (51 files)
<b>Use Case:</b> All files from a specific upload session

<b>Example 2: Multiple Ranges</b>
<b>Input:</b> <code>100-120, 150-170</code>
<b>Result:</b> Messages 100-120 AND 150-170 (42 files)
<b>Use Case:</b> Two separate collections

<b>Example 3: Specific Files</b>
<b>Input:</b> <code>105, 110, 115, 120</code>
<b>Result:</b> Only messages 105, 110, 115, 120 (4 files)
<b>Use Case:</b> Handpicked important files

<b>Example 4: Mixed Format</b>
<b>Input:</b> <code>100-105, 110, 115-120, 125</code>
<b>Result:</b> Messages 100-105, 110, 115-120, 125 (14 files)
<b>Use Case:</b> Combination of ranges and specific files

<b>Example 5: Large Collection</b>
<b>Input:</b> <code>1000-1100, 1200-1250</code>
<b>Result:</b> Messages 1000-1100 AND 1200-1250 (152 files)
<b>Use Case:</b> Multiple albums or categories

<b>⚠️ Common Mistakes to Avoid:</b>

❌ <code>100 - 150</code> (spaces in range)
✅ <code>100-150</code>

❌ <code>100-150 200-250</code> (missing comma)
✅ <code>100-150, 200-250</code>

❌ <code>150-100</code> (reverse range)
✅ <code>100-150</code>

❌ <code>abc-xyz</code> (non-numeric)
✅ <code>100-150</code>

<b>💡 Pro Tips:</b>

1️⃣ <b>Organize by Category:</b>
   Movies: <code>1000-1050</code>
   Shows: <code>2000-2100</code>
   Create separate links for each

2️⃣ <b>Skip Deleted Files:</b>
   If message 105 is deleted:
   <code>100-104, 106-110</code>

3️⃣ <b>Premium Content:</b>
   <code>500, 505, 510</code>
   Only share specific premium files

4️⃣ <b>Season Packs:</b>
   Season 1: <code>1001-1010</code>
   Season 2: <code>1011-1020</code>
   Separate links per season

<b>📊 Limit:</b> Maximum 200 messages per link

<b>Ready to create? Use:</b> <code>/custom_batch</code>
"""
    
    await message.reply_text(examples, quote=True)
