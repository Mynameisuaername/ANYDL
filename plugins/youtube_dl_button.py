#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import asyncio
import json
import math
import os
import shutil
import time
from datetime import datetime

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
from helper_funcs.help_uploadbot import DownLoadFile
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image
from helper_funcs.help_Nekmo_ffmpeg import generate_screen_shots
from helper_funcs.ran_text import random_char
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument

async def youtube_dl_call_back(bot, update):
    cb_data = update.data

    # youtube_dl extractors
    tg_send_type, youtube_dl_format, youtube_dl_ext, sz = cb_data.split("|")
    szz, msd_id = sz.rsplit(' ', 1)
    try:
        int(szz)
    except:
        pass
    '''if type(szz) is int and szz > Config.TG_MAX_FILE_SIZE:
        try:
            await update.answer('Choosen video is bigger than Telegram upload limit.')
        except Exception as anss:
            print(anss)
            pass'''

    # print(cb_data, update.message.id, msd_id)

    random1 = random_char(5)
    thumb_image_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ' ' + str(msd_id) + ".jpg"
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(msd_id) + '/' + str(update.from_user.id) + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except (FileNotFoundError) as e:
        print(e, 'json file not found')
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=update.message.id,
            revoke=True
        )
        return False
    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = str(response_json.get("title")) + \
        "_" + youtube_dl_format + "." + youtube_dl_ext
    youtube_dl_username = None
    youtube_dl_password = None
    if "|" in youtube_dl_url:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        # https://stackoverflow.com/a/761825/4723940
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
        logger.info(youtube_dl_url)
        logger.info(custom_file_name)
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    cbv = str(szz) + "//" + str(msd_id)
    ina = InlineKeyboardMarkup([ [InlineKeyboardButton("Check Progress", callback_data=cbv)], ])
    await bot.edit_message_caption(
        caption=Translation.DOWNLOAD_START,
        chat_id=update.message.chat.id,
        message_id=update.message.id,
        reply_markup=ina
    )
    description = Translation.CUSTOM_CAPTION_UL_FILE
    if "fulltitle" in response_json:
        description = response_json['fulltitle'][0:1021]
        description = f"<a href = '{youtube_dl_url}'> {description} </a>"
        # escape Markdown and special characters
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + "/" + str(msd_id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--prefer-ffmpeg",
            "--extract-audio",
            "--no-check-certificates",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        # command_to_exec = ["yt-dlp", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--embed-subs", "--ignore-config",
            "--no-check-certificates",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    command_to_exec.append("--no-warnings")
    # command_to_exec.append("--quiet")
    logger.info(command_to_exec)
    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    logger.info(e_response)
    logger.info(t_response)
    ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=error_message
        )
        return False

    if t_response:
        logger.info(t_response)
        try:
            os.remove(save_ytdl_json_path)
        except FileNotFoundError as exc:
            pass
        end_one = datetime.now()
        time_taken_for_download = (end_one -start).seconds
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            print('Except block enterance')
            # print("\n", os.listdir(lia), "Line 217")
            lia=os.listdir(tmp_directory_for_each_user)
            print(lia)
            if lia[0].rsplit(".", 1)[1] == "json":
                download_directory = tmp_directory_for_each_user + '/' + lia[1]
                print("---------", lia, '---------')
            else:
                download_directory = tmp_directory_for_each_user + '/' + lia[0]
            # download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size
        try:
            if tg_send_type == 'video' and 'webm' in download_directory:
                ownload_directory = download_directory.rsplit('.', 1)[0] + '.mkv'
                os.rename(download_directory, ownload_directory)
                download_directory = ownload_directory
        except:
            pass

        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                message_id=update.message.id
            )
        else:
            is_w_f = False
            '''images = await generate_screen_shots(
                download_directory,
                tmp_directory_for_each_user,
                is_w_f,
                Config.DEF_WATER_MARK_FILE,
                300,
                9
            )
            logger.info(images)'''
            await bot.edit_message_caption(
                caption=Translation.UPLOAD_START,
                chat_id=update.message.chat.id,
                message_id=update.message.id
            )
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            width = 0
            height = 0
            duration = 0
            if tg_send_type != "file":
                metadata = extractMetadata(createParser(download_directory))
                if metadata is not None:
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                if tg_send_type == "vm":
                    height = width
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                if tg_send_type == "file":
                    img.resize((320, height))
                else:
                    img.resize((90, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
                
            else:
                thumb_image_path = None
            start_time = time.time()
            # try to upload file
            if tg_send_type == "audio":
                await bot.edit_message_media(
                    chat_id=update.message.chat.id,
                    media=InputMediaAudio(media=download_directory, caption=description, duration=duration, thumb=thumb_image_path, parse_mode=pyrogram.enums.ParseMode.HTML),
                    # caption=description,
                    # parse_mode=pyrogram.enums.ParseMode.HTML,
                    # duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    # thumb=thumb_image_path,
                    # reply_to_message_id=update.message.reply_to_message.id,
                    message_id=update.message.id
                    # progress=progress_for_pyrogram,
                    # progress_args=(
                    #     Translation.UPLOAD_START,
                    #     update.message,
                    #     start_time
                    # )
                )
            elif tg_send_type == "file":
                await bot.edit_message_media(
                    chat_id=update.message.chat.id,
                    media=InputMediaDocument(media=download_directory, caption=description, thumb=thumb_image_path, parse_mode=pyrogram.enums.ParseMode.HTML),
                    # thumb=thumb_image_path,
                    # caption=description,
                    # parse_mode=pyrogram.enums.ParseMode.HTML,
                    # reply_markup=reply_markup,
                    # reply_to_message_id=update.message.reply_to_message.id,
                    message_id=update.message.id
                )
            elif tg_send_type == "vm":
                await bot.send_video_note(
                    chat_id=update.message.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "video":
                await bot.edit_message_media(
                    chat_id=update.message.chat.id,
                    media=InputMediaVideo(media=download_directory, caption=description, width=width, height=height, duration=duration, thumb=thumb_image_path, supports_streaming=True, parse_mode=pyrogram.enums.ParseMode.HTML),
                    # caption=description,
                    # parse_mode=pyrogram.enums.ParseMode.HTML,
                    # duration=duration,
                    # width=width,
                    # height=height,
                    # supports_streaming=True,
                    # reply_markup=reply_markup,
                    # thumb=thumb_image_path,
                    # reply_to_message_id=update.message.reply_to_message.id,
                    message_id=update.message.id
                )
            else:
                logger.info("Did this happen? :\\")
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            #
            '''media_album_p = []
            if images is not None:
                i = 0
                caption = "JOIN : https://t.me/TGBotsCollection \n For the List of Telegram Bots"
                if is_w_f:
                    caption = "/upgrade to Plan D to remove the watermark\nJOIN : https://t.me/TGBotsCollection \n For the List of Telegram Bots"
                for image in images:
                    if os.path.exists(image):
                        if i == 0:
                            media_album_p.append(
                                pyrogram.types.InputMediaPhoto(
                                    media=image,
                                    caption=caption,
                                    parse_mode=pyrogram.enums.ParseMode.HTML
                                )
                            )
                        else:
                            media_album_p.append(
                                pyrogram.types.InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
            await bot.send_media_group(
                chat_id=update.message.chat.id,
                disable_notification=True,
                reply_to_message_id=update.message.id,
                media=media_album_p
            )'''
            #
            try:
                os.remove(thumb_image_path)
                shutil.rmtree(tmp_directory_for_each_user)
            except:
                pass

            '''await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                disable_web_page_preview=True
            )'''
