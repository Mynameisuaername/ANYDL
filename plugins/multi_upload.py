#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from datetime import datetime
import os
from os import walk

import requests
import subprocess
import time
import shutil
import asyncio

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.ran_text import random_char

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@pyrogram.Client.on_message(pyrogram.filters.command(["playlist"]))
async def get_link(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    logger.info(update.from_user)
    
    h5rd = random_char(5)
    a = await bot.send_message(
          chat_id=update.chat.id,
          text=f"Downloading Playlist...",
          reply_to_message_id=update.message_id
    )
    tox = update.text
    download_location = Config.DOWNLOAD_LOCATION + "/" + f"{h5rd}" + "/"
    os.makedirs(download_location)
    logger.info(tox)
    url = tox.split(" ")[1]
    print(update.chat.id, update.message_id)
    command_to_exec = []
    start = datetime.now()

    command_to_exec = [
        'yt-dlp',
        '-c',
        '--max-filesize', '2147483648',
        '--embed-subs', 
        '--yes-playlist',
        '--hls-prefer-ffmpeg',
        '-f', '136+140',
        url,
        '-o',
        download_location
    ]        
  
    logger.info(command_to_exec)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    logger.info(e_response)
    logger.info(t_response)
    
    filenames = next(walk(download_location), (None, None, []))[2]  # [] if no file
    c_time = time.time()
    noss = len(filenames)
    print(noss)
    logger.info(filenames)
    nn = 0
    while nn < noss:
      d_loc = download_location + filenames[nn]
      logger.info(d_loc)
      try:
        await bot.send_document(
            chat_id=update.chat.id,
            document=d_loc,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.UPLOAD_START,
                a,
                c_time
            )
        )
      except Exception as e:
        print(e)
        pass
      nn = nn + 1
          
    await bot.edit_message_text(
        text=f"Playlist Uploaded!",
        chat_id=update.chat.id,
        message_id=a.message_id,
        disable_web_page_preview=True  
    )
    
    
