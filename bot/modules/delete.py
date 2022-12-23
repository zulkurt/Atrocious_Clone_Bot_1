from threading import Thread
from telegram.ext import CommandHandler

from bot import dispatcher, LOGGER

from bot.modules.helper_funcs.mirror_helpers.message_utils import auto_delete_message, sendMessage
from bot.modules.helper_funcs.mirror_helpers.filters import CustomFilters
from bot.modules.helper_funcs.mirror_helpers.bot_commands import BotCommands
from bot.modules.helper_funcs.mirror_helpers.gdriveTools import GoogleDriveHelper
from bot.modules.helper_funcs.mirror_helpers.bot_utils import is_gdrive_link


def deletefile(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    if len(args) > 1:
        link = args[1]
    elif reply_to is not None:
        link = reply_to.text
    else:
        link = ""
    if is_gdrive_link(link):
        LOGGER.info(link)
        drive = GoogleDriveHelper()
        msg = drive.deletefile(link)
    else:
        msg = ("Send Gdrive link along with command or by replying to the link by command")
    reply_message = sendMessage(msg, context.bot, update.message)
    Thread(target=auto_delete_message, args=(context.bot, update.message, reply_message)).start()


delete_handler = CommandHandler(command=BotCommands.DeleteCommand, callback=deletefile, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
dispatcher.add_handler(delete_handler)