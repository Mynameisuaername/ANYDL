#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
import shutil

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

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


@pyrogram.Client.on_message(pyrogram.filters.command(["c2f"]))
async def convert_to_audio(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.id,
            revoke=True
        )
        return
    if (update.reply_to_message is not None) and (update.reply_to_message.media is not None) :
        rn2 = random_char(5)
        download_location = Config.DOWNLOAD_LOCATION + "/" + rn2 + "/"
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_FILE,
            reply_to_message_id=update.id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_FILE,
                a,
                c_time
            )
        )
        if the_real_download_location is None:
            await bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.chat.id,
                message_id=a.id
            )
        else:
            # don't care about the extension
            # convert video to audio format
            # audio_file_location_path = the_real_download_location
            # await a.delete()
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.UPLOAD_START,
                message_id=a.id
            )
            logger.info(the_real_download_location)
            caption=the_real_download_location.rsplit("/", 1)[1]
            caption=caption.rsplit(".", 1)[0]
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "_" + ".jpg"
            if not os.path.exists(thumb_image_path):
                thumb_image_path = None
            else:
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # get the correct width, height, and duration for videos greater than 10MB
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                img.resize((90, 90))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            # try to upload file
            c_time = time.time()
            await bot.send_document(
                chat_id=update.chat.id,
                document=the_real_download_location,
                caption=caption,
                # performer="",
                # title="",
                # reply_markup=reply_markup,
                thumb=thumb_image_path,
                reply_to_message_id=update.reply_to_message.id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    a, 
                    c_time
                )
            )
            try:
                # os.remove(thumb_image_path)
                # os.remove(the_real_download_location)
                # os.remove(audio_file_location_path)
                shutil.rmtree(download_location)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=a.id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_FOR_C2V,
            reply_to_message_id=update.id
        )
