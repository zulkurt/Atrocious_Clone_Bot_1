from random import SystemRandom
from string import ascii_letters, digits

from bot import download_dict, download_dict_lock, LOGGER, STOP_DUPLICATE, STORAGE_THRESHOLD
from bot.modules.helper_funcs.mirror_helpers.gdriveTools import GoogleDriveHelper
from bot.modules.helper_funcs.mirror_helpers.gd_download_status import GdDownloadStatus
from bot.modules.helper_funcs.mirror_helpers.message_utils import sendMessage, sendStatusMessage, sendMarkup
from bot.modules.helper_funcs.mirror_helpers.bot_utils import get_readable_file_size
from bot.modules.helper_funcs.mirror_helpers.fs_utils import get_base_name, check_storage_threshold


def add_gd_download(link, listener, is_gdtot, is_unified, is_udrive, is_sharer, is_sharedrive, is_filepress, new_name=None):
    res, size, name, files = GoogleDriveHelper().helper(link)
    if res != "":
        return sendMessage(res, listener.bot, listener.message)
    if STOP_DUPLICATE and not listener.isLeech:
        LOGGER.info("Checking File/Folder if already in Drive...")
        if listener.isZip:
            gname = name + ".zip"
        elif listener.extract:
            try:
                gname = get_base_name(name)
            except:
                gname = None
        if gname is not None:
            gmsg, button = GoogleDriveHelper().drive_list(gname, True)
            if gmsg:
                msg = "File/Folder is already available in Drive.\nHere are the search results:"
                return sendMarkup(msg, listener.bot, listener.message, button)
    if STORAGE_THRESHOLD:
        arch = any([listener.extract, listener.isZip])
        limit = None
        if STORAGE_THRESHOLD is not None:
            acpt = check_storage_threshold(size, arch)
            if not acpt:
                msg = f"You must leave {STORAGE_THRESHOLD}GB free storage."
                msg += f"\nYour File/Folder size is {get_readable_file_size(size)}"
                return sendMessage(msg, listener.bot, listener.message)
    LOGGER.info(f"Download Name: {name}")
    drive = GoogleDriveHelper(name, listener)
    gid = "".join(SystemRandom().choices(ascii_letters + digits, k=12))
    download_status = GdDownloadStatus(drive, size, listener, gid)
    with download_dict_lock:
        download_dict[listener.uid] = download_status
    listener.onDownloadStart()
    sendStatusMessage(listener.message, listener.bot)
    drive.download(link,new_name)
    if (is_gdtot or is_unified or is_udrive or is_sharer or is_sharedrive or is_filepress):
        drive.deletefile(link)
