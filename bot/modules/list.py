from threading import Thread
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import LOGGER, dispatcher

from bot.modules.helper_funcs.mirror_helpers.gdriveTools import GoogleDriveHelper
from bot.modules.helper_funcs.mirror_helpers.message_utils import sendMessage, editMessage, sendMarkup
from bot.modules.helper_funcs.mirror_helpers.filters import CustomFilters
from bot.modules.helper_funcs.mirror_helpers.bot_commands import BotCommands
from bot.modules.helper_funcs.mirror_helpers.button_build import ButtonMaker

def list_buttons(update, context):
    user_id = update.message.from_user.id
    if len(update.message.text.split(" ", maxsplit=1)) < 2:
        return sendMessage('Send a search key along with command', context.bot, update.message)
    buttons = ButtonMaker()
    buttons.sbutton("Folders", f"types {user_id} folders")
    buttons.sbutton("Files", f"types {user_id} files")
    buttons.sbutton("Both", f"types {user_id} both")
    buttons.sbutton("Cancel", f"types {user_id} cancel")
    button = InlineKeyboardMarkup(buttons.build_menu(2))
    sendMarkup('Choose option to list.', context.bot, update.message, button)

def select_type(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    msg = query.message
    key = msg.reply_to_message.text.split(" ", maxsplit=1)[1]
    data = query.data
    data = data.split(" ")
    if user_id != int(data[1]):
        return query.answer(text="Not Yours!", show_alert=True)
    elif data[2] == 'cancel':
        query.answer()
        return editMessage("list has been canceled!", msg)
    query.answer()
    item_type = data[2]
    editMessage(f"<b>Searching for <i>{key}</i></b>", msg)
    Thread(target=_list_drive, args=(key, msg, item_type)).start()

def _list_drive(key, bmsg, item_type):
    LOGGER.info(f"listing: {key}")
    gdrive = GoogleDriveHelper()
    msg, button = gdrive.drive_list(key, isRecursive=True, itemType=item_type)
    if button:
        editMessage(msg, bmsg, button)
    else:
        editMessage(f'No result found for <i>{key}</i>', bmsg)

list_handler = CommandHandler(BotCommands.ListCommand, list_buttons, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
list_type_handler = CallbackQueryHandler(select_type, pattern="types", run_async=True)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(list_type_handler)