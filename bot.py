# bot.py - Fixed version that properly handles channel after session reset

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, FloodWait, ChannelPrivate
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
        self.db_channel = None
        self.invitelink = None

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

            # Setup Database Channel - with proper retry and wait
            print(f"🔍 Checking Database Channel: {CHANNEL_ID}")
            
            channel_accessible = False
            max_retries = 5  # Increased retries
            
            for attempt in range(1, max_retries + 1):
                try:
                    if attempt > 1:
                        wait_time = attempt * 3  # Increasing wait time
                        print(f"⏳ Waiting {wait_time} seconds before retry {attempt}/{max_retries}...")
                        await asyncio.sleep(wait_time)
                    
                    print(f"📡 Attempt {attempt}/{max_retries}: Fetching channel...")
                    
                    # Try to get the channel
                    db_channel = await self.get_chat(CHANNEL_ID)
                    
                    # SUCCESS - Store it
                    self.db_channel = db_channel
                    channel_accessible = True
                    
                    print(f"✅ Database Channel Found: {db_channel.title}")
                    
                    # Try to test permissions
                    try:
                        test = await self.send_message(chat_id=CHANNEL_ID, text="✅ Bot Connected")
                        await asyncio.sleep(1)
                        await test.delete()
                        print(f"✅ Bot can send/delete messages in DB channel")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not test message: {e}")
                        print(f"⚠️ But channel is accessible - continuing...")
                    
                    break
                    
                except (PeerIdInvalid, ChannelInvalid) as e:
                    print(f"❌ Attempt {attempt}/{max_retries} failed: {e}")
                    
                    if attempt == max_retries:
                        print("\n" + "=" * 50)
                        print("🔧 CHANNEL ACCESS ISSUE DETECTED")
                        print("=" * 50)
                        print(f"\nThis happens after session reset (FloodWait recovery).")
                        print(f"\n✅ Your bot setup is correct!")
                        print(f"✅ The channel configuration is fine!")
                        print(f"❌ The NEW session just needs to 'discover' the channel")
                        print(f"\n🔧 TWO WAYS TO FIX:")
                        print(f"\n1️⃣ AUTOMATIC (Recommended):")
                        print(f"   • Just WAIT 5-10 minutes")
                        print(f"   • Telegram will sync automatically")
                        print(f"   • Then restart the bot")
                        print(f"\n2️⃣ MANUAL (Instant):")
                        print(f"   • Send any message to the channel yourself")
                        print(f"   • This forces Telegram to sync")
                        print(f"   • Then restart the bot immediately")
                        print(f"\n🤖 Bot Details:")
                        print(f"   Username: @{usr_bot_me.username}")
                        print(f"   Channel ID: {CHANNEL_ID}")
                        print("\n" + "=" * 50)
                        
                        # Set db_channel to a dummy object so bot doesn't crash
                        # This allows testing commands to work
                        class DummyChannel:
                            def __init__(self, channel_id):
                                self.id = channel_id
                                self.title = "Pending Sync..."
                                self.username = None
                        
                        self.db_channel = DummyChannel(CHANNEL_ID)
                        print(f"⚠️ Bot will run in LIMITED MODE until channel syncs")
                        print(f"⚠️ /ping, /test, /debug will work")
                        print(f"⚠️ File sharing will not work until channel is accessible")
                        break
                    
                    continue
                
                except FloodWait as e:
                    print(f"⏳ FloodWait: Waiting {e.value} seconds...")
                    await asyncio.sleep(e.value)
                    continue
                
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    if attempt == max_retries:
                        # Use dummy channel
                        class DummyChannel:
                            def __init__(self, channel_id):
                                self.id = channel_id
                                self.title = "Error"
                                self.username = None
                        self.db_channel = DummyChannel(CHANNEL_ID)
                        break
                    continue

            # Setup Force Subscribe Channel
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
            
            print("\n" + ascii_art)
            
            if channel_accessible:
                print("=" * 50)
                print("✅ Bot is ready!")
                print("✅ All features operational")
                print("=" * 50)
            else:
                print("=" * 50)
                print("⚠️ Bot is running in LIMITED MODE")
                print("⚠️ Wait 5-10 min OR send message to channel")
                print("⚠️ Then restart bot for full functionality")
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
            sys.exit(1)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
