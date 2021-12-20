from pyrogram import Client, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import psutil
import time
from speedtest import Speedtest
bot_start_time = time.time()

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
def speed_convert(size):
    """Hi human, you can't read bytes?"""
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "MB/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@Client.on_message(filters.command(["server"]), group=-2)
async def start(client, message):
    try:
    	print(message)
    except Exception as ww:
    	print(ww)
    	pass

    bot_uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot_start_time)) 
    joinButton = InlineKeyboardMarkup([
        [InlineKeyboardButton("JOIN", url="https://t.me/TGBotsCollection")],
        [InlineKeyboardButton(
            "Try", url="https://t.me/TGBotsCollectionbot")]
    ])
    welcomed = f"<b>--Server Details--</b>\n<b>CPU:</b> {psutil.cpu_percent()}%\n<b>RAM:</b> {psutil.virtual_memory().percent}%\n<b>DISK:</b> {psutil.disk_usage('/').percent}%\n\n <b><i>Bot Uptime :</i></b> {bot_uptime}"
    await message.reply_text(welcomed, reply_markup=joinButton)
    raise StopPropagation

@Client.on_message(filters.command(["Speedtest"]) & filters.privte)
async def speedd(client, message):
	try:
		spg = await bot.send_message(text=f'Running speedtest....', chat_id=update.chat.id, reply_to_message_id=update.message_id,)
	except Exception as er:
		print(er)
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
    	print(test)
    except Exception as ere:
    	print(ere)
    	pass
    string_speed = f'''
<b>Server</b>
<b>Name:</b> <code>{result['server']['name']}</code>
<b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
<b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
    
<b>SpeedTest Results</b>
<b>Upload:</b> <code>{speed_convert(result['upload'] / 8)}</code>
<b>Download:</b>  <code>{speed_convert(result['download'] / 8)}</code>
<b>Ping:</b> <code>{result['ping']} ms</code>
<b>ISP:</b> <code>{result['client']['isp']}</code>
'''

    spg.delete()
    try:
        update.message_id.reply_photo(path, string_speed, parse_mode=ParseMode.HTML)
    except Exception as cv:
    	print("Error ", cv)
        update.message_id.reply_text(string_speed, parse_mode=ParseMode.HTML)



