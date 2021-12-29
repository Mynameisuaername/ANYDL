#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import json
import math
import os
import shutil
import subprocess
import time

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.display_progress import progress_for_pyrogram, humanbytes
from plugins.youtube_dl_button import youtube_dl_call_back
from plugins.dl_button import ddl_call_back
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


@pyrogram.Client.on_callback_query()
async def button(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=update.message.message_id,
            revoke=True
        )
        return
    # logger.info(update)
    cb_data = update.data
    if ":" in cb_data:
        # unzip formats
        extract_dir_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + "zipped" + "/"
        if not os.path.isdir(extract_dir_path):
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=update.message.message_id,
                revoke=True
            )
            return False
        zip_file_contents = os.listdir(extract_dir_path)
        type_of_extract, index_extractor, undefined_tcartxe = cb_data.split(":")
        if index_extractor == "NONE":
            try:
                shutil.rmtree(extract_dir_path)
            except:
                pass
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.CANCEL_STR,
                message_id=update.message.message_id
            )
        elif index_extractor == "ALL":
            i = 0
            for file_content in zip_file_contents:
                current_file_name = os.path.join(extract_dir_path, file_content)
                start_time = time.time()
                await bot.send_document(
                    chat_id=update.message.chat.id,
                    document=current_file_name,
                    # thumb=thumb_image_path,
                    caption=file_content,
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
                i = i + 1
                os.remove(current_file_name)
            try:
                shutil.rmtree(extract_dir_path)
            except:
                pass
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.ZIP_UPLOADED_STR.format(i, "0"),
                message_id=update.message.message_id
            )
        else:
            file_content = zip_file_contents[int(index_extractor)]
            current_file_name = os.path.join(extract_dir_path, file_content)
            start_time = time.time()
            await bot.send_document(
                chat_id=update.message.chat.id,
                document=current_file_name,
                # thumb=thumb_image_path,
                caption=file_content,
                # reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update.message,
                    start_time
                )
            )
            try:
                shutil.rmtree(extract_dir_path)
            except:
                pass
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.ZIP_UPLOADED_STR.format("1", "0"),
                message_id=update.message.message_id
            )
    elif "|" in cb_data:
        await youtube_dl_call_back(bot, update)
    elif "=" in cb_data:
        await ddl_call_back(bot, update)
    elif "//" in cb_data:
        szze, ms_id = cb_data.rsplit('//', 1)
        print('\n\n', cb_data, 'cb_buttons')
        download_directory = Config.DOWNLOAD_LOCATION + "/" + str(ms_id)
        smze = 0
        ToStr = ' •• '.join(map(str, os.listdir(download_directory)))
        await bot.send_message(chat_id = update.message.chat.id, text=ToStr)
        #print(os.listdir(download_directory), "cb_buttons")
        if not os.path.isdir(download_directory):
            siio='This file is not present in the directory!'
            await update.answer(siio)
            '''elif:
            for ele in os.scandir(download_directory):
                smze+=os.path.getsize(ele)
            if smze>int(cb_data.split("//")[1])*1.2:
                await update.answer("Video Downloded Successfully. \n\n Now Downloading audio", show_alert="True")
             elif:
            for ele in os.scandir(download_directory):
                smze+=os.path.getsize(ele)
            if smze>int(cb_data.split("//")[1]):
                await update.answer("Video, audio downloaded sucessfully. \n\n Upload starts soon.", show_alert="True")'''
        elif len(os.listdir(download_directory)) == 4:
            print(len(os.listdir(download_directory)), os.listdir(download_directory))
            await update.answer("Video & Audio downloaded sucessfully\n\nUploading starts soon. . .")
        elif "N/A" in cb_data:
            #szze = "N/A"
            for ele in os.scandir(download_directory):
                smze+=os.path.getsize(ele)
                siio = humanbytes(int(smze))
            await update.answer(f'Downloaded: {siio} of {"N/A"}')
        else:
            for ele in os.scandir(download_directory):
                smze+=os.path.getsize(ele)
                siio = humanbytes(int(smze))
            print('Type of smze:', type(smze), '\n', 'Type of siio:', type(siio))
            if int(smze)<int(szze):
                await update.answer(f'Downloaded: {siio} of {humanbytes(int(szze))}')
            else:
                diff = int(smze)-int(szze)
                await update.answer(f'Video Downloded Successfully: {humanbytes(int(szze))} \n\n Now Downloading audio: {humanbytes(diff)}', show_alert="True")
                
