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
import moviepy.editor as pp

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
from helper_funcs.help_Nekmo_ffmpeg import exa_audio

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image

async def list_to_async_iterator(my_list):
    for item in my_list:
        yield item  # Use 'yield' to signal items asynchronously

@pyrogram.Client.on_message(pyrogram.filters.command(["c2a"]))
async def convert_to_audio(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.id,
            revoke=True
        )
        return
    if (update.reply_to_message is not None) and (update.reply_to_message.media is not None) :
        rnom = random_char(5)
        download_location = f"{Config.DOWNLOAD_LOCATION}/{str(update.from_user.id)}/{str(update.id)}" + "/"
        ab=await bot.send_message(
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
                ab,
                c_time
            )
        )
        if the_real_download_location is not None:
            await bot.edit_message_text(
                text=f"Video Download Successfully, now trying to convert into Audio. \n\n⌛️Wait for some time.",
                chat_id=update.chat.id,
                message_id=ab.id
            )
            time.sleep(0.5)
            auddio= await exa_audio(download_location, update.id, the_real_download_location)
            if auddio is not None:
                logger.info(auddio)
                await bot.edit_message_text(
                    text=Translation.UPLOAD_START,
                    chat_id=update.chat.id,
                    message_id=ab.id
                )
                async for audio in list_to_async_iterator(auddio):
                    metadata = extractMetadata(createParser(audio))
                    duration=None
                    # if metadata.has('duration'):
                    if metadata:
                        duration=metadata.get("duration",None)
                        if duration: duration.seconds
                    await bot.send_audio(
                        chat_id=update.chat.id,
                        audio=audio,
                        # supports_streaming=True,
                        reply_to_message_id=update.id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            Translation.UPLOAD_START,
                            ab,
                            c_time
                        )
                    )
            # don't care about the extension
            # convert video to audio format
            '''f_name = the_real_download_location.rsplit('/',1)[-1]
            clip = pp.VideoFileClip(the_real_download_location)
            clip.audio.write_audiofile(f_name+'.mp3')
            audio_file_location = f_name+'.mp3'
            logger.info(audio_file_location)'''
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            try:
                # os.remove(thumb_image_path)
                shutil.rmtree(str(download_location))
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=ab.id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"**Reply** with a telegram video file to convert.",
            reply_to_message_id=update.id
        )
