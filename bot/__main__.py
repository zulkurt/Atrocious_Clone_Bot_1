from time import time
from pyrogram import idle
from sys import executable
from signal import signal, SIGINT
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from telegram import InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler

from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, LOGGER, Interval, OWNER_ID, AUTHORIZED_CHATS
from bot.modules.helper_funcs.mirror_helpers.fs_utils import start_cleanup, clean_all, exit_clean_up
from bot.modules.helper_funcs.mirror_helpers.telegraph_helper import telegraph
from bot.modules.helper_funcs.mirror_helpers.bot_utils import get_readable_file_size, get_readable_time
from bot.modules.helper_funcs.mirror_helpers.bot_commands import BotCommands
from bot.modules.helper_funcs.mirror_helpers.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from bot.modules.helper_funcs.mirror_helpers.filters import CustomFilters
from bot.modules.helper_funcs.mirror_helpers.button_build import ButtonMaker

from bot.modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, delete, count, shell


def stats(update, context):
    if ospath.exists(".git"):
        last_commit = check_output(
            ["git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'"],
            shell=True,
        ).decode()
    else:
        last_commit = "No UPSTREAM_REPO"
    currentTime = get_readable_time(time() - botStartTime)
    osUptime = get_readable_time(time() - boot_time())
    total, used, free, disk = disk_usage("/")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = (
        f"<b>Commit Date:</b> {last_commit}\n\n"
        f"<b>Bot Uptime:</b> {currentTime}\n"
        f"<b>OS Uptime:</b> {osUptime}\n\n"
        f"<b>Total Disk Space:</b> {total}\n"
        f"<b>Used:</b> {used} | <b>Free:</b> {free}\n\n"
        f"<b>Upload:</b> {sent}\n"
        f"<b>Download:</b> {recv}\n\n"
        f"<b>CPU:</b> {cpuUsage}%\n"
        f"<b>RAM:</b> {mem_p}%\n"
        f"<b>DISK:</b> {disk}%\n\n"
        f"<b>Physical Cores:</b> {p_core}\n"
        f"<b>Total Cores:</b> {t_core}\n\n"
        f"<b>SWAP:</b> {swap_t} | <b>Used:</b> {swap_p}%\n"
        f"<b>Memory Total:</b> {mem_t}\n"
        f"<b>Memory Free:</b> {mem_a}\n"
        f"<b>Memory Used:</b> {mem_u}\n")
    sendMessage(stats, context.bot, update.message)


def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Mirror Group", "https://t.me/+Xwwi7toV4YsyMWJl")
    buttons.buildbutton("Support Group", "https://t.me/AtrociousBotSupport")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f"""
This bot can clone google drive , gdtot, hubdrive, katdrive, and filepress link and upload telegram file in google drive .
Type /{BotCommands.HelpCommand} to get a list of available commands
"""
        sendMarkup(start_string, context.bot, update.message, reply_markup)
    else:
        sendMarkup(
            "Not Authorized user, deploy your own clone bot",
            context.bot,
            update.message,
            reply_markup)


def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
    clean_all()
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update.message)
    end_time = int(round(time() * 1000))
    editMessage(f"{end_time - start_time} ms", reply)


def log(update, context):
    sendLogFile(context.bot, update.message)


help_string = f"""
/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersCommand}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner)

/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner)

/{BotCommands.RestartCommand}: Restart and update the bot

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.ShellCommand}: Run commands in Shell (Only Owner)

/{BotCommands.CloneCommand}: Clone google drive , gdtot, hubdrive, katdrive, and filepress file 

/{BotCommands.CountCommand}: Count google drive files

/{BotCommands.DeleteCommand}: Delete google drive files

/{BotCommands.ListCommand}: Search files in google drive

/{BotCommands.StatusCommand}: Check bot current status 

/{BotCommands.StatsCommand}: Check bot stats
"""


def bot_help(update, context):
    sendMessage(help_string, context.bot, update.message)


def main():
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        osremove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand, bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand, stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

app.start()
main()
idle()
