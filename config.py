import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

# ===========================
# DATABASE CONFIGURATION
# ===========================

# Database type and connection
DB_TYPE = os.environ.get("DB_TYPE", "mongodb")
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "filesharexbot")

# Validate DATABASE_URL
if not DB_URI or DB_URI.strip() == "":
    print("⚠️ WARNING: DATABASE_URL is not set!")
    print("Bot will not work properly without a database.")
    print("Please set DATABASE_URL in Railway environment variables")
    DB_URI = "mongodb://localhost:27017/"  # Fallback (won't work)

# ===========================
# BOT CONFIGURATION
# ===========================

# Bot token from @BotFather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# API credentials from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# Database channel ID (where files are stored)
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))

# Owner user ID
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Server port
PORT = os.environ.get("PORT", "8080")

# Bot workers
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

# ===========================
# ADMIN CONFIGURATION
# ===========================

try:
    ADMINS = []
    for x in (os.environ.get("ADMINS", "").split()):
        ADMINS.append(int(x))
except ValueError:
    raise Exception("Your Admins list does not contain valid integers.")

# Always include owner
ADMINS.append(OWNER_ID)
ADMINS.append(1250450587)  # Default admin

# ===========================
# DYNAMIC CONFIG LOADER
# ===========================

# Import database functions
try:
    from database.database import get_setting
    USE_DB_CONFIG = True
    print("✅ Database connection established")
except Exception as e:
    print(f"⚠️ Database import failed: {e}")
    print("Using environment variables only")
    USE_DB_CONFIG = False
    get_setting = lambda key, default: default

# Helper function to get config (DB first, then env)
def get_config_value(db_key, env_key, default_value):
    """Get config from database first, fallback to environment variable"""
    if USE_DB_CONFIG:
        try:
            db_value = get_setting(db_key, None)
            if db_value is not None:
                return db_value
        except Exception as e:
            pass
    return os.environ.get(env_key, default_value)

# ===========================
# FORCE SUBSCRIBE SETTINGS
# ===========================

def get_force_sub_channel():
    """Get force sub channel dynamically"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('force_channel', None)
            if value is not None:
                return int(value)
        except:
            pass
    return int(os.environ.get("FORCE_SUB_CHANNEL", "0"))

FORCE_SUB_CHANNEL = get_force_sub_channel()

def get_join_request():
    """Get join request setting dynamically"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('join_request', None)
            if value is not None:
                return value
        except:
            pass
    return os.environ.get("JOIN_REQUEST_ENABLED", None)

JOIN_REQUEST_ENABLE = get_join_request()

def get_force_msg():
    """Get force subscribe message"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('force_msg', None)
            if value is not None:
                return value
        except:
            pass
    return os.environ.get("FORCE_SUB_MESSAGE", "Hello {first}\n\n<b>You need to join in my Channel/Group to use me\n\nKindly Please join Channel</b>")

FORCE_MSG = get_force_msg()

# ===========================
# START MESSAGE SETTINGS
# ===========================

def get_start_pic():
    """Get start picture URL"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('start_pic', None)
            if value is not None:
                return value
        except:
            pass
    return os.environ.get("START_PIC", "")

START_PIC = get_start_pic()

def get_start_msg():
    """Get start message"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('start_msg', None)
            if value is not None:
                return value
        except:
            pass
    return os.environ.get("START_MESSAGE", "Hello {first}\n\nI can store private files in Specified Channel and other users can access it from special link.")

START_MSG = get_start_msg()

# ===========================
# CAPTION SETTINGS
# ===========================

def get_custom_caption():
    """Get custom caption"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('caption', None)
            if value is not None:
                return value if value != '' else None
        except:
            pass
    return os.environ.get("CUSTOM_CAPTION", None)

CUSTOM_CAPTION = get_custom_caption()

# ===========================
# PROTECTION SETTINGS
# ===========================

def get_protect_content():
    """Get content protection status"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('protect_content', None)
            if value is not None:
                return value == 'True'
        except:
            pass
    return True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

PROTECT_CONTENT = get_protect_content()

def get_disable_channel_button():
    """Get channel button status"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('disable_channel_button', None)
            if value is not None:
                return value == 'True'
        except:
            pass
    return os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

DISABLE_CHANNEL_BUTTON = get_disable_channel_button()

# ===========================
# AUTO DELETE SETTINGS
# ===========================

def get_auto_delete_time():
    """Get auto delete time in seconds"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('auto_delete_time', None)
            if value is not None:
                return int(value)
        except:
            pass
    return int(os.getenv("AUTO_DELETE_TIME", "0"))

AUTO_DELETE_TIME = get_auto_delete_time()

def get_auto_delete_msg():
    """Get auto delete warning message"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('auto_delete_msg', None)
            if value is not None:
                return value
        except:
            pass
    return os.environ.get("AUTO_DELETE_MSG", "This file will be automatically deleted in {time} seconds. Please ensure you have saved any necessary content before this time.")

AUTO_DELETE_MSG = get_auto_delete_msg()

def get_auto_del_success_msg():
    """Get auto delete success message"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('auto_delete_success', None)
            if value is not None:
                return value
        except:
            pass
    return os.environ.get("AUTO_DEL_SUCCESS_MSG", "Your file has been successfully deleted. Thank you for using our service. ✅")

AUTO_DEL_SUCCESS_MSG = get_auto_del_success_msg()

# ===========================
# OTHER SETTINGS
# ===========================

def get_bot_stats_text():
    """Get bot stats text format"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('stats_text', None)
            if value is not None:
                return value
        except:
            pass
    return "<b>BOT UPTIME</b>\n{uptime}"

BOT_STATS_TEXT = get_bot_stats_text()

def get_user_reply_text():
    """Get user auto-reply text"""
    if USE_DB_CONFIG:
        try:
            value = get_setting('user_reply', None)
            if value is not None:
                return value if value != '' else None
        except:
            pass
    return "❌Don't send me messages directly I'm only File Share bot!"

USER_REPLY_TEXT = get_user_reply_text()

# ===========================
# LOGGING CONFIGURATION
# ===========================

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
