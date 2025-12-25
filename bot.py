# bot.py - FIXED VERSION with proper channel initialization

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
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

            # CRITICAL FIX: Access database channel FIRST to populate peer cache
            try:
                print(f"🔍 Checking Database Channel: {CHANNEL_ID}")
                
                # Method 1: Try to get chat directly
                db_channel = await self.get_chat(CHANNEL_ID)
                self.db_channel = db_channel
                
                print(f"✅ Database Channel Found: {db_channel.title}")
                
                # Test sending and deleting message
                try:
                    test = await self.send_message(chat_id=CHANNEL_ID, text="✅ Bot Started - Connection Test")
                    await test.delete()
                    print(f"✅ Bot can send/delete messages in DB channel")
                except Exception as e:
                    print(f"⚠️ Warning: Could not test message send/delete: {e}")
                    print(f"⚠️ Make sure bot has proper admin permissions")
                
            except Exception as e:
                self.LOGGER(__name__).error(f"Database Channel Error: {e}")
                print("=" * 50)
                print("❌ DATABASE CHANNEL ERROR!")
                print(f"❌ Channel ID: {CHANNEL_ID}")
                print(f"❌ Error: {e}")
                print("=" * 50)
                print("⚠️ CRITICAL: Bot cannot work without DB Channel")
                print("⚠️ SOLUTIONS:")
                print("1. Verify channel ID is correct (use @userinfobot)")
                print("2. Make sure bot is ADDED to the channel first")
                print("3. Make bot admin with all permissions")
                print("4. Restart bot after adding to channel")
                print("5. Try /verify command to diagnose issues")
                print("=" * 50)
                self.LOGGER(__name__).info("\n⚠️ Bot Stopped. Join https://t.me/CodeXBotzSupport for support")
                sys.exit()

            # Check Force Sub Channel (AFTER database channel is working)
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
                        self.LOGGER(__name__).warning(f"Could not get invite link: {link_error}")
                        self.invitelink = None
                        print(f"⚠️ Bot cannot create invite link")
                        print(f"⚠️ Enable 'Invite Users via Link' permission")
                        
                except Exception as e:
                    self.LOGGER(__name__).error(f"Force Sub Channel Error: {e}")
                    print("=" * 50)
                    print("❌ FORCE SUBSCRIBE CHANNEL ERROR!")
                    print(f"❌ Channel ID: {FORCE_SUB_CHANNEL}")
                    print(f"❌ Error: {e}")
                    print("=" * 50)
                    print("⚠️ SOLUTIONS:")
                    print("1. Check if FORCE_SUB_CHANNEL ID is correct")
                    print("2. Add bot to force sub channel")
                    print("3. Make bot admin with 'Invite Users' permission")
                    print("4. Or set FORCE_SUB_CHANNEL=0 to disable")
                    print("=" * 50)
                    self.invitelink = None
                    print("⚠️ Bot will continue without force subscribe")
            else:
                self.invitelink = None
                print("📢 Force Subscribe: Disabled")

            self.set_parse_mode(ParseMode.HTML)
            self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
            print(ascii_art)
            print("Welcome to CodeXBotz File Sharing Bot")
            print(f"Bot is ready to receive messages!")
            print("=" * 50)
            
            # Start web server
            try:
                app = web.AppRunner(await web_server())
                await app.setup()
                bind_address = "0.0.0.0"
                await web.TCPSite(app, bind_address, PORT).start()
                print(f"✅ Web server started on port {PORT}")
                print("=" * 50)
            except Exception as e:
                print(f"⚠️ Web server error (non-critical): {e}")
            
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ Error during startup: {e}")
            print(f"❌ STARTUP ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
        print("👋 Bot stopped gracefully")
