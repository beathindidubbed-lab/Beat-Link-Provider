# bot.py - Version with retry logic for Railway

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, FloodWait
import sys
import asyncio
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT

ascii_art = """
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        try:
            await super().start()
            usr_bot_me = await self.get_me()
            self.uptime = datetime.now()
            self.username = usr_bot_me.username
            
            print("=" * 50)
            print(f"✅ Bot started successfully!")
            print(f"📱 Bot Username: @{usr_bot_me.username}")
            print(f"🆔 Bot ID: {usr_bot_me.id}")
            print("=" * 50)

            # RETRY LOGIC for database channel
            max_retries = 3
            retry_delay = 5
            
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"🔍 Attempt {attempt}/{max_retries}: Checking Database Channel: {CHANNEL_ID}")
                    
                    # Wait a moment for Telegram to sync
                    if attempt > 1:
                        print(f"⏳ Waiting {retry_delay} seconds before retry...")
                        await asyncio.sleep(retry_delay)
                    
                    db_channel = await self.get_chat(CHANNEL_ID)
                    self.db_channel = db_channel
                    
                    print(f"✅ Database Channel Found: {db_channel.title}")
                    
                    # Test sending and deleting message
                    try:
                        test = await self.send_message(chat_id=CHANNEL_ID, text="✅ Bot Connected - Test Message")
                        await asyncio.sleep(1)
                        await test.delete()
                        print(f"✅ Bot can send/delete messages in DB channel")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not test message: {e}")
                    
                    # If we got here, channel access is working
                    break
                    
                except (PeerIdInvalid, ChannelInvalid) as e:
                    if attempt == max_retries:
                        self.LOGGER(__name__).error(f"Database Channel Error after {max_retries} attempts: {e}")
                        print("=" * 50)
                        print("❌ DATABASE CHANNEL ERROR!")
                        print(f"❌ Channel ID: {CHANNEL_ID}")
                        print(f"❌ Error: {e}")
                        print("=" * 50)
                        print("⚠️ CRITICAL: Bot cannot access DB Channel")
                        print("⚠️ POSSIBLE CAUSES:")
                        print("1. Bot was just added - Telegram needs time to sync")
                        print("2. Session is cached - try redeploying")
                        print("3. Channel ID is incorrect")
                        print("4. Bot is not actually in the channel")
                        print("=" * 50)
                        print("⚠️ SOLUTIONS:")
                        print("1. Wait 5-10 minutes after adding bot")
                        print("2. Redeploy on Railway to get fresh session")
                        print("3. Double-check channel ID with @userinfobot")
                        print("4. Remove bot from channel, then add again")
                        print("=" * 50)
                        sys.exit()
                    else:
                        print(f"⚠️ Channel not accessible yet, retrying...")
                        continue
                
                except FloodWait as e:
                    print(f"⏳ FloodWait: Waiting {e.x} seconds...")
                    await asyncio.sleep(e.x)
                    continue
                
                except Exception as e:
                    if attempt == max_retries:
                        self.LOGGER(__name__).error(f"Unexpected error: {e}")
                        print(f"❌ Unexpected error: {e}")
                        sys.exit()
                    continue

            # Check Force Sub Channel
            if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL != 0:
                try:
                    print(f"🔍 Checking Force Subscribe Channel: {FORCE_SUB_CHANNEL}")
                    
                    force_channel = await self.get_chat(FORCE_SUB_CHANNEL)
                    print(f"📢 Force Sub Channel: {force_channel.title}")
                    
                    try:
                        link = force_channel.invite_link
                        if not link:
                            link = await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        self.invitelink = link
                        print(f"✅ Invite Link: {link[:50]}...")
                    except Exception as link_error:
                        self.invitelink = None
                        print(f"⚠️ Could not create invite link: {link_error}")
                        
                except Exception as e:
                    self.invitelink = None
                    print(f"⚠️ Force Sub Channel error: {e}")
                    print("⚠️ Bot will continue without force subscribe")
            else:
                self.invitelink = None
                print("📢 Force Subscribe: Disabled")

            self.set_parse_mode(ParseMode.HTML)
            self.LOGGER(__name__).info(f"Bot Running..!")
            print(ascii_art)
            print("Bot is ready!")
            print("=" * 50)
            
            # Start web server
            try:
                app = web.AppRunner(await web_server())
                await app.setup()
                bind_address = "0.0.0.0"
                await web.TCPSite(app, bind_address, PORT).start()
                print(f"✅ Web server started on port {PORT}")
            except Exception as e:
                print(f"⚠️ Web server error: {e}")
            
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ Startup error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
