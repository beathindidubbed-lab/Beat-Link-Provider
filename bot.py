# bot.py - FIXED VERSION with better error handling

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
            
            print("=" * 50)
            print(f"✅ Bot started successfully!")
            print(f"📱 Bot Username: @{usr_bot_me.username}")
            print(f"🆔 Bot ID: {usr_bot_me.id}")
            print("=" * 50)

            # Check Force Sub Channel (with better error handling)
            if FORCE_SUB_CHANNEL and FORCE_SUB_CHANNEL != 0:
                try:
                    # Try to get channel info
                    force_channel = await self.get_chat(FORCE_SUB_CHANNEL)
                    print(f"📢 Force Sub Channel: {force_channel.title} ({FORCE_SUB_CHANNEL})")
                    
                    # Try to get invite link
                    try:
                        link = force_channel.invite_link
                        if not link:
                            link = await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        self.invitelink = link
                        print(f"✅ Force Sub Invite Link: {link[:50]}...")
                    except Exception as link_error:
                        self.LOGGER(__name__).warning(f"Could not get invite link: {link_error}")
                        self.invitelink = None
                        print(f"⚠️ Warning: Bot cannot create invite link")
                        print(f"⚠️ Make sure bot has 'Invite Users via Link' permission")
                        
                except Exception as e:
                    self.LOGGER(__name__).error(f"Force Sub Channel Error: {e}")
                    print("=" * 50)
                    print("❌ FORCE SUBSCRIBE CHANNEL ERROR!")
                    print(f"❌ Error: {e}")
                    print(f"❌ Channel ID: {FORCE_SUB_CHANNEL}")
                    print("=" * 50)
                    print("⚠️ SOLUTIONS:")
                    print("1. Check if FORCE_SUB_CHANNEL ID is correct")
                    print("2. Make sure bot is added to the channel")
                    print("3. Make bot admin with 'Invite Users' permission")
                    print("4. Or set FORCE_SUB_CHANNEL=0 to disable")
                    print("=" * 50)
                    
                    # Continue running but set invitelink to None
                    self.invitelink = None
                    print("⚠️ Bot will continue but force subscribe won't work")
            else:
                self.invitelink = None
                print("📢 Force Subscribe: Disabled")
            
            # Check Database Channel
            try:
                db_channel = await self.get_chat(CHANNEL_ID)
                self.db_channel = db_channel
                
                # Test sending message
                test = await self.send_message(chat_id=db_channel.id, text="✅ Bot Started - Test Message")
                await test.delete()
                
                print(f"✅ Database Channel: {db_channel.title} ({CHANNEL_ID})")
                print(f"✅ Bot can send/delete messages")
                
            except Exception as e:
                self.LOGGER(__name__).error(f"Database Channel Error: {e}")
                print("=" * 50)
                print("❌ DATABASE CHANNEL ERROR!")
                print(f"❌ Error: {e}")
                print(f"❌ Channel ID: {CHANNEL_ID}")
                print("=" * 50)
                print("⚠️ CRITICAL: Bot cannot work without DB Channel")
                print("⚠️ SOLUTIONS:")
                print("1. Create a private channel")
                print("2. Add bot to channel")
                print("3. Make bot admin with all permissions")
                print("4. Get channel ID (forward message to @userinfobot)")
                print("5. Set CHANNEL_ID in environment variables")
                print("=" * 50)
                self.LOGGER(__name__).info("\n⚠️ Bot Stopped. Join https://t.me/CodeXBotzSupport for support")
                sys.exit()

            self.set_parse_mode(ParseMode.HTML)
            self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
            print(ascii_art)
            print("Welcome to CodeXBotz File Sharing Bot")
            print(f"Bot is ready to receive messages!")
            print("=" * 50)
            
            self.username = usr_bot_me.username
            
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
