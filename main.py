import asyncio
import os
from bot import Bot
from pyrogram import idle
from pyrogram.errors import FloodWait

async def start_services():
    # IMPORTANT: Don't delete session files unless absolutely necessary
    # Deleting sessions causes FloodWait errors
    
    # Only uncomment this if you need to force a fresh session
    # session_files = ['Bot.session', 'Bot.session-journal']
    # for file in session_files:
    #     if os.path.exists(file):
    #         os.remove(file)
    #         print(f"🗑️ Deleted old session file: {file}")
    
    try:
        app = Bot()
        await app.start()
        print("\n✅ Bot started successfully! Press Ctrl+C to stop.\n")
        await idle()
        await app.stop()
    except FloodWait as e:
        print(f"\n{'='*70}")
        print(f"⏳ FLOOD WAIT ERROR - TELEGRAM RATE LIMIT")
        print(f"{'='*70}")
        print(f"\n⏱️  Required wait time: {e.value} seconds (~{e.value//60} minutes)")
        print(f"\n❓ Why did this happen?")
        print(f"   • Session file was deleted and recreated too many times")
        print(f"   • Multiple bot instances tried to connect simultaneously")
        print(f"   • Too many authorization attempts in short time")
        print(f"\n💡 How to fix:")
        print(f"   1. Wait {e.value//60} minutes before restarting the bot")
        print(f"   2. DON'T delete Bot.session files (they prevent this)")
        print(f"   3. Don't run multiple instances of the bot")
        print(f"   4. If available, restore a valid Bot.session file")
        print(f"\n🔧 Auto-wait option:")
        print(f"   Uncomment the auto-wait code in main.py to wait automatically")
        print(f"{'='*70}\n")
        
        # AUTO-WAIT OPTION (uncomment to enable)
        # This will make the bot wait automatically instead of exiting
        # 
        # print(f"⏳ Auto-waiting for {e.value} seconds...")
        # print(f"   Started at: {datetime.now().strftime('%H:%M:%S')}")
        # await asyncio.sleep(e.value)
        # print(f"   Finished at: {datetime.now().strftime('%H:%M:%S')}")
        # print("✅ Wait complete! Attempting to restart...")
        # await start_services()  # Recursive retry
        
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
