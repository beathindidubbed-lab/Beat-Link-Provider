import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

DB_TYPE = os.environ.get("DB_TYPE", "mongodb")  # mongodb, postgresql, mysql, sqlite
DB_URI = os.environ.get("DB_URI", "your_connection_string")
DB_NAME = os.environ.get("DB_NAME", "your_db_name")

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "0"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

#Port
PORT = os.environ.get("PORT", "8080")

#Database 
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "filesharexbot")

# Import database functions for dynamic config
try:
    from database.database import get_setting
    USE_DB_CONFIG = True
except:
    USE_DB_CONFIG = False
    get_setting = lambda key, default: default

# Helper function to get config (DB first, then env)
def get_config(key, env_var, default):
    """Get config from database first, fallback to environment variable"""
    if USE_DB_CONFIG:
        db_value = get_setting(key, None)
        if db_value is not None:
            return db_value
    return os.environ.get(env_var, default)

#force sub channel id, if you want enable force sub
def get_force_sub_channel():
    """Get force sub channel dynamically"""
    if USE_DB_CONFIG:
        value = get_setting('force_channel', None)
        if value is not None:
            try:
                return int(value)
            except:
                pass
    return int(os.environ.get("FORCE_SUB_CHANNEL", "0"))

FORCE_SUB_CHANNEL = get_force_sub_channel()

def get_join_request():
    """Get join request setting dynamically"""
    if USE_DB_CONFIG:
        value = get_setting('join_request', None)
        if value is not None:
            return value
    return os.environ.get("JOIN_REQUEST_ENABLED", None)

JOIN_REQUEST_ENABLE = get_join_request()

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#start message
def get_start_pic():
    if USE_DB_CONFIG:
        value = get_setting('start_pic', None)
        if value is not None:
            return value
    return os.environ.get("START_PIC", "")

START_PIC = get_start_pic()

def get_start_msg():
    if USE_DB_CONFIG:
        value = get_setting('start_msg', None)
        if value is not None:
            return value
    return os.environ.get("START_MESSAGE", "Hello {first}\n\nI can store private files in Specified Channel and other users can access it from special link.")

START_MSG = get_start_msg()

try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
def get_force_msg():
    if USE_DB_CONFIG:
        value = get_setting('force_msg', None)
        if value is not None:
            return value
    return os.environ.get("FORCE_SUB_MESSAGE", "Hello {first}\n\n<b>You need to join in my Channel/Group to use me\n\nKindly Please join Channel</b>")

FORCE_MSG = get_force_msg()

#set your Custom Caption here, Keep None for Disable Custom Caption
def get_custom_caption():
    if USE_DB_CONFIG:
        value = get_setting('caption', None)
        if value is not None:
            return value if value != '' else None
    return os.environ.get("CUSTOM_CAPTION", None)

CUSTOM_CAPTION = get_custom_caption()

#set True if you want to prevent users from forwarding files from bot
def get_protect_content():
    if USE_DB_CONFIG:
        value = get_setting('protect_content', None)
        if value is not None:
            return value == 'True'
    return True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

PROTECT_CONTENT = get_protect_content()

# Auto delete time in seconds.
def get_auto_delete_time():
    if USE_DB_CONFIG:
        value = get_setting('auto_delete_time', None)
        if value is not None:
            try:
                return int(value)
            except:
                pass
    return int(os.getenv("AUTO_DELETE_TIME", "0"))

AUTO_DELETE_TIME = get_auto_delete_time()

def get_auto_delete_msg():
    if USE_DB_CONFIG:
        value = get_setting('auto_delete_msg', None)
        if value is not None:
            return value
    return os.environ.get("AUTO_DELETE_MSG", "This file will be automatically deleted in {time} seconds. Please ensure you have saved any necessary content before this time.")

AUTO_DELETE_MSG = get_auto_delete_msg()

def get_auto_del_success_msg():
    if USE_DB_CONFIG:
        value = get_setting('auto_delete_success', None)
        if value is not None:
            return value
    return os.environ.get("AUTO_DEL_SUCCESS_MSG", "Your file has been successfully deleted. Thank you for using our service. ✅")

AUTO_DEL_SUCCESS_MSG = get_auto_del_success_msg()

#Set true if you want Disable your Channel Posts Share button
def get_disable_channel_button():
    if USE_DB_CONFIG:
        value = get_setting('disable_channel_button', None)
        if value is not None:
            return value == 'True'
    return os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

DISABLE_CHANNEL_BUTTON = get_disable_channel_button()

def get_bot_stats_text():
    if USE_DB_CONFIG:
        value = get_setting('stats_text', None)
        if value is not None:
            return value
    return "<b>BOT UPTIME</b>\n{uptime}"

BOT_STATS_TEXT = get_bot_stats_text()

def get_user_reply_text():
    if USE_DB_CONFIG:
        value = get_setting('user_reply', None)
        if value is not None:
            return value if value != '' else None
    return "❌Don't send me messages directly I'm only File Share bot!"

USER_REPLY_TEXT = get_user_reply_text()

ADMINS.append(OWNER_ID)
ADMINS.append(1250450587)

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