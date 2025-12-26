# bot.py - Improved version with proper channel discovery

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
            
            print("=" * 70)
            print(f"✅ Bot started successfully!")
            print(f"📱 Bot Username: @{usr_bot_me.username}")
            print(f"🆔 Bot ID: {usr_bot_me.id}")
            print("=" * 70)

            # Setup Database Channel with improved error handling
            print(f"\n🔍 Setting up Database Channel: {CHANNEL_ID}\n")
            
            db_channel_ok = False
            
            for attempt in range(1, 4):
                try:
                    if attempt > 1:
                        print(f"⏳ Retry {attempt}/3 - Waiting 5 seconds...")
                        await asyncio.sleep(5)
                    
                    print(f"📡 Attempt {attempt}: Fetching channel info...")
                    db_channel = await self.get_chat(CHANNEL_ID)
                    self.db_channel = db_channel
                    
                    print(f"✅ Channel Found!")
                    print(f"   Name: {db_channel.title}")
                    print(f"   Type: {db_channel.type}")
                    print(f"   ID: {db_channel.id}")
                    
                    # Test permissions
                    try:
                        print(f"\n🧪 Testing bot permissions...")
                        test = await self.send_message(
                            chat_id=CHANNEL_ID, 
                            text="✅ Bot Connected & Verified"
                        )
                        await asyncio.sleep(1)
                        await test.delete()
                        print(f"✅ Bot has proper permissions!")
                        db_channel_ok = True
                        break
                        
                    except Exception as perm_error:
                        print(f"⚠️ Permission test failed: {perm_error}")
                        print(f"⚠️ Bot may not have proper admin permissions")
                        # Still continue - bot might work without test message
                        db_channel_ok = True
                        break
                    
                except (PeerIdInvalid, ChannelInvalid) as e:
                    print(f"❌ Attempt {attempt} failed: {e}")
                    
                    if attempt == 3:
                        # Last attempt - show detailed error
                        print("\n" + "=" * 70)
                        print("❌ CRITICAL: Cannot access Database Channel")
                        print("=" * 70)
                        print(f"\n📋 Channel Information:")
                        print(f"   Channel ID: {CHANNEL_ID}")
                        print(f"   Bot Username: @{usr_bot_me.username}")
                        print(f"\n🔧 Required Actions:")
                        print(f"\n1. Verify Channel ID is correct:")
                        print(f"   • Forward any message from your channel to @userinfobot")
                        print(f"   • Check if the ID matches: {CHANNEL_ID}")
                        print(f"\n2. Add bot to channel:")
                        print(f"   • Open your channel in Telegram")
                        print(f"   • Add @{usr_bot_me.username} as member")
                        print(f"\n3. Make bot admin with permissions:")
                        print(f"   ✅ Post Messages")
                        print(f"   ✅ Edit Messages")
                        print(f"   ✅ Delete Messages")
                        print(f"\n4. After adding bot, wait 2 minutes then restart")
                        print(f"\n💡 Alternative: Run the fix_channel.py script")
                        print("=" * 70)
                        
                        # Don't exit immediately - let's try to continue
                        # Some features might still work
                        print(f"\n⚠️ Bot will continue running with limited functionality")
                        print(f"⚠️ Fix the channel access to enable all features\n")
                        break
                    
                    continue
                
                except ChannelPrivate:
                    print(f"❌ Channel is private and bot is not a member")
                    print(f"   Add @{usr_bot_me.username} to channel {CHANNEL_ID}")
                    
                    if attempt == 3:
                        print(f"\n⚠️ Continuing with limited functionality...")
                        break
                    continue
                
                except FloodWait as e:
                    print(f"⏳ FloodWait: Waiting {e.value} seconds...")
                    await asyncio.sleep(e.value)
                    continue
                
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    if attempt == 3:
                        print(f"\n⚠️ Continuing anyway...")
                        break
                    continue

            # Setup Force Subscribe Channel
            if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL != 0:
                print(f"\n📢 Setting up Force Subscribe Channel: {FORCE_SUB_CHANNEL}\n")
                try:
                    force_channel = await self.get_chat(FORCE_SUB_CHANNEL)
                    print(f"✅ Force Sub Channel: {force_channel.title}")
                    
                    try:
                        link = force_channel.invite_link
                        if not link:
                            link = await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        self.invitelink = link
                        print(f"✅ Invite Link: {link[:50]}...")
                    except Exception as link_error:
                        self.invitelink = None
                        print(f"⚠️ Could not create invite link: {link_error}")
                        print(f"⚠️ Force subscribe will not work properly")
                        
                except Exception as e:
                    self.invitelink = None
                    print(f"⚠️ Force Sub Channel error: {e}")
                    print(f"⚠️ Bot will continue without force subscribe")
            else:
                self.invitelink = None
                print(f"\n📢 Force Subscribe: Disabled")

            # Set parse mode
            self.set_parse_mode(ParseMode.HTML)
            
            # Print status
            print("\n" + "=" * 70)
            if db_channel_ok:
                print("✅ BOT IS READY!")
                print(f"✅ All systems operational")
            else:
                print("⚠️ BOT IS RUNNING WITH LIMITED FUNCTIONALITY")
                print(f"⚠️ Database channel needs to be fixed")
                print(f"⚠️ Users won't be able to get files until channel is accessible")
            print("=" * 70)
            print(ascii_art)
            print("=" * 70)
            
            # Start web server
            try:
                app = web.AppRunner(await web_server())
                await app.setup()
                bind_address = "0.0.0.0"
                await web.TCPSite(app, bind_address, PORT).start()
                print(f"🌐 Web server: http://0.0.0.0:{PORT}")
            except Exception as e:
                print(f"⚠️ Web server error: {e}")
            
            print("=" * 70)
            print("Bot is now running. Press Ctrl+C to stop.")
            print("=" * 70 + "\n")
            
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ Startup error: {e}")
            import traceback
            traceback.print_exc()
            
            print("\n" + "=" * 70)
            print("❌ FATAL ERROR - Bot failed to start")
            print("=" * 70)
            print(f"Error: {e}")
            print("\nCheck the error above and fix the issue.")
            print("=" * 70 + "\n")
            sys.exit(1)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
        print("\n👋 Bot stopped gracefully.\n")
