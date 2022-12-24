import os

from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from socket import setdefaulttimeout
from faulthandler import enable as faulthandler_enable
from telegram.ext import Updater as tgUpdater
from os import remove as osremove, path as ospath, environ
from requests import get as rget
from json import loads as jsnloads
from subprocess import run as srun, check_output
from time import sleep, time
from threading import Thread, Lock
from pyrogram import Client, enums
from dotenv import load_dotenv

faulthandler_enable()
setdefaulttimeout(600)
botStartTime = time()

if ospath.exists('log.txt'):
    with open('log.txt', 'w+') as f:
        f.truncate(0)

basicConfig(format="%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s", handlers=[FileHandler("log.txt"), StreamHandler()], level=INFO)

LOGGER = getLogger(__name__)
load_dotenv("config.env", override=True)

def getConfig(name: str):
    return environ[name]


Interval = []
DRIVES_NAMES = []
DRIVES_IDS = []
INDEX_URLS = []

try:
    if bool(getConfig("_____REMOVE_THIS_LINE_____")):
        log_error("The README.md file there to be read! Exiting now!")
        exit()
except:
    pass

DOWNLOAD_DIR = None
BOT_TOKEN = None

download_dict_lock = Lock()
status_reply_dict_lock = Lock()
# Key: update.effective_chat.id
# Value: telegram.Message
status_reply_dict = {}
# Key: update.message.message_id
# Value: An object of Status
download_dict = {}
# key: rss_title
rss_dict = {}

AUTHORIZED_CHATS = set()
AS_DOC_USERS = set()
AS_MEDIA_USERS = set()
EXTENTION_FILTER = set()
SUDO_USERS = set()

try:
    aid = getConfig("AUTHORIZED_CHATS")
    aid = aid.split(" ")
    for _id in aid:
        AUTHORIZED_CHATS.add(int(_id))
except:
    pass
try:
    aid = getConfig("SUDO_USERS")
    aid = aid.split(" ")
    for _id in aid:
        SUDO_USERS.add(int(_id))
except:
    pass
try:
    fx = getConfig("EXTENTION_FILTER")
    if len(fx) > 0:
        fx = fx.split(" ")
        for x in fx:
            EXTENTION_FILTER.add(x.lower())
except:
    pass

try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    GDRIVE_ID = getConfig("GDRIVE_ID")
    DOWNLOAD_DIR = os.path.abspath(".") + "/" + getConfig("DOWNLOAD_DIR")
    if not DOWNLOAD_DIR.endswith("/"):
        DOWNLOAD_DIR = DOWNLOAD_DIR + "/"
    DOWNLOAD_STATUS_UPDATE_INTERVAL = int(getConfig("DOWNLOAD_STATUS_UPDATE_INTERVAL"))
    OWNER_ID = int(getConfig("OWNER_ID"))
    AUTO_DELETE_MESSAGE_DURATION = int(getConfig("AUTO_DELETE_MESSAGE_DURATION"))
    TELEGRAM_API = getConfig("TELEGRAM_API")
    TELEGRAM_HASH = getConfig("TELEGRAM_HASH")
except:
    pass


LOGGER.info("Generating BOT_SESSION_STRING")
app = Client(name='pyrogram', api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, bot_token=BOT_TOKEN, parse_mode=enums.ParseMode.HTML, no_updates=True)

try:
    BUTTON_FOUR_NAME = getConfig("BUTTON_FOUR_NAME")
    BUTTON_FOUR_URL = getConfig("BUTTON_FOUR_URL")
    if len(BUTTON_FOUR_NAME) == 0 or len(BUTTON_FOUR_URL) == 0:
        raise KeyError
except:
    BUTTON_FOUR_NAME = None
    BUTTON_FOUR_URL = None

try:
    BUTTON_FIVE_NAME = getConfig("BUTTON_FIVE_NAME")
    BUTTON_FIVE_URL = getConfig("BUTTON_FIVE_URL")
    if len(BUTTON_FIVE_NAME) == 0 or len(BUTTON_FIVE_URL) == 0:
        raise KeyError
except:
    BUTTON_FIVE_NAME = None
    BUTTON_FIVE_URL = None

try:
    BUTTON_SIX_NAME = getConfig("BUTTON_SIX_NAME")
    BUTTON_SIX_URL = getConfig("BUTTON_SIX_URL")
    if len(BUTTON_SIX_NAME) == 0 or len(BUTTON_SIX_URL) == 0:
        raise KeyError
except:
    BUTTON_SIX_NAME = None
    BUTTON_SIX_URL = None

try:
    CLONE_LIMIT = getConfig("CLONE_LIMIT")
    if len(CLONE_LIMIT) == 0:
        raise KeyError
    CLONE_LIMIT = float(CLONE_LIMIT)
except:
    CLONE_LIMIT = None

try:
    CMD_INDEX = getConfig("CMD_INDEX")
    if len(CMD_INDEX) == 0:
        raise KeyError
except:
    CMD_INDEX = ""

try:
    DB_URI = getConfig("DATABASE_URL")
    if len(DB_URI) == 0:
        raise KeyError
except:
    DB_URI = None

try:
    DRIVEFIRE_CRYPT = getConfig("DRIVEFIRE_CRYPT")
    if len(DRIVEFIRE_CRYPT) == 0:
        raise KeyError
except:
    DRIVEFIRE_CRYPT = None

try:
    GDTOT_CRYPT = getConfig("GDTOT_CRYPT")
    if len(GDTOT_CRYPT) == 0:
        raise KeyError
except:
    GDTOT_CRYPT = None

try:
    HUBDRIVE_CRYPT = getConfig("HUBDRIVE_CRYPT")
    if len(HUBDRIVE_CRYPT) == 0:
        raise KeyError
except:
    HUBDRIVE_CRYPT = None

try:
    IGNORE_PENDING_REQUESTS = getConfig("IGNORE_PENDING_REQUESTS")
    IGNORE_PENDING_REQUESTS = IGNORE_PENDING_REQUESTS.lower() == "true"
except:
    IGNORE_PENDING_REQUESTS = False

try:
    INCOMPLETE_TASK_NOTIFIER = getConfig("INCOMPLETE_TASK_NOTIFIER")
    INCOMPLETE_TASK_NOTIFIER = INCOMPLETE_TASK_NOTIFIER.lower() == "true"
except:
    INCOMPLETE_TASK_NOTIFIER = False

try:
    INDEX_URL = getConfig("INDEX_URL").rstrip("/")
    if len(INDEX_URL) == 0:
        raise KeyError
    INDEX_URLS.append(INDEX_URL)
except:
    INDEX_URL = None
    INDEX_URLS.append(None)

try:
    IS_TEAM_DRIVE = getConfig("IS_TEAM_DRIVE")
    IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == "true"
except:
    IS_TEAM_DRIVE = False

try:
    laravel_session = getConfig("laravel_session")
    if len(laravel_session) == 0:
        raise KeyError
except:
    laravel_session = None

try:
    KATDRIVE_CRYPT = getConfig("KATDRIVE_CRYPT")
    if len(KATDRIVE_CRYPT) == 0:
        raise KeyError
except:
    KATDRIVE_CRYPT = None

try:
    STATUS_LIMIT = getConfig("STATUS_LIMIT")
    if len(STATUS_LIMIT) == 0:
        raise KeyError
    STATUS_LIMIT = int(STATUS_LIMIT)
except:
    STATUS_LIMIT = None

try:
    STOP_DUPLICATE = getConfig("STOP_DUPLICATE")
    STOP_DUPLICATE = STOP_DUPLICATE.lower() == "true"
except:
    STOP_DUPLICATE = False

try:
    STORAGE_THRESHOLD = getConfig("STORAGE_THRESHOLD")
    if len(STORAGE_THRESHOLD) == 0:
        raise KeyError
    STORAGE_THRESHOLD = float(STORAGE_THRESHOLD)
except:
    STORAGE_THRESHOLD = None

try:
    SHAREDRIVE_PHPCKS = getConfig("SHAREDRIVE_PHPCKS")
    if len(SHAREDRIVE_PHPCKS) == 0:
        raise KeyError
except:
    SHAREDRIVE_PHPCKS = None

try:
    SHORTENER = getConfig("SHORTENER")
    SHORTENER_API = getConfig("SHORTENER_API")
    if len(SHORTENER) == 0 or len(SHORTENER_API) == 0:
        raise KeyError
except:
    SHORTENER = None
    SHORTENER_API = None

try:
    UNIFIED_EMAIL = getConfig("UNIFIED_EMAIL")
    if len(UNIFIED_EMAIL) == 0:
        raise KeyError
except:
    UNIFIED_EMAIL = None

try:
    UNIFIED_PASS = getConfig("UNIFIED_PASS")
    if len(UNIFIED_PASS) == 0:
        raise KeyError
except:
    UNIFIED_PASS = None

try:
    USE_SERVICE_ACCOUNTS = getConfig("USE_SERVICE_ACCOUNTS")
    USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == "true"
except:
    USE_SERVICE_ACCOUNTS = False

try:
    VIEW_LINK = getConfig("VIEW_LINK")
    VIEW_LINK = VIEW_LINK.lower() == "true"
except:
    VIEW_LINK = False

try:
    XSRF_TOKEN = getConfig("XSRF_TOKEN")
    if len(XSRF_TOKEN) == 0:
        raise KeyError
except:
    XSRF_TOKEN = None

if ospath.exists('accounts.zip'):
    if ospath.exists('accounts'):
        srun(["rm", "-rf", "accounts"])
    srun(["unzip", "-q", "-o", "accounts.zip"])
    srun(["chmod", "-R", "777", "accounts"])
    osremove('accounts.zip')

DRIVES_NAMES.append("Main")
DRIVES_IDS.append(GDRIVE_ID)
if ospath.exists("drive_folder"):
    with open("drive_folder", "r+") as f:
        lines = f.readlines()
        for line in lines:
            try:
                temp = line.strip().split()
                DRIVES_IDS.append(temp[1])
                DRIVES_NAMES.append(temp[0].replace("_", " "))
            except:
                pass
            try:
                INDEX_URLS.append(temp[2])
            except:
                INDEX_URLS.append(None)

updater = tgUpdater(token=BOT_TOKEN, request_kwargs={"read_timeout": 20, "connect_timeout": 15})
bot = updater.bot
dispatcher = updater.dispatcher
job_queue = updater.job_queue
botname = bot.username
