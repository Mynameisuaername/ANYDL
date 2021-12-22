from pyrogram import Client, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import psutil, shutil
import time
from helper_funcs.display_progress import humanbytes
from speedtest import Speedtest

bot_start_time = time.time()

'''  welcomed = f"<b>--Server Details--</b>\n<b>CPU:</b> {psutil.cpu_percent()}%\n<b>RAM:</b> {psutil.virtual_memory().percent}%\n<b>DISK:</b> {psutil.disk_usage('/').percent}%\n\n <b><i>Bot Uptime :</i></b> {bot_uptime}"
    await message.reply_text(welcomed, reply_markup=joinButton)'''

''' def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result '''

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
        await update.reply_photo(path, string_speed, parse_mode="HTML")
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
