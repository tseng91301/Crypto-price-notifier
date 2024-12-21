import discord
from discord.ext import commands
import asyncio

import json

import bit_price_alert as ba

conf = json.loads(open("conf/api_settings.json", 'r').read())

# 機器人 Token
TOKEN = conf['token']
N_CHANNEL_ID = int(conf["notify_channel_id"])
S_CHANNEL_ID = int(conf["settings_msg_channel_id"])

# Intents 設置（確保機器人有權限讀取消息）
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

# 創建 Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot 啟動事件
@bot.event
async def on_ready():
    print(f'機器人已登錄為 {bot.user}')
    # 啟動背景任務
    bot.loop.create_task(periodic_notification())

# 發送通知指令
@bot.command()
async def notify(ctx, *, message):
    await ctx.send(f"通知：{message}")

# 手動發送給特定頻道
async def send_notification(channel_id, message):
    channel = bot.get_channel(channel_id)  # 獲取頻道對象
    if channel:
        await channel.send(message)
    else:
        print("找不到指定的頻道。")

async def periodic_notification():
    await bot.wait_until_ready()  # 確保 Bot 啟動完成
    print("Start message sending demo")
    channel = bot.get_channel(N_CHANNEL_ID)
    while not bot.is_closed():
        if channel:
            if(ba.notify_queue.qsize() > 0):
                print("Notifying...")
                last_notify = ba.notify_queue.get()
                # {"s": v["s"], "p": v["p"], "d": "d"}
                notify_str = last_notify["s"] + " Alert: "
                if last_notify["d"] == "u":
                    notify_str += "Goes above "
                elif last_notify["d"] == "d":
                    notify_str += "Falls below "
                else:
                    notify_str += "Triggers "
                notify_str += str(last_notify["p"])
                try:
                    notify_str += ", " + last_notify["m"]
                except:
                    pass
                await channel.send(notify_str)
        await asyncio.sleep(0.5)  # 每小時發送一次

# 接收所有訊息事件
@bot.event
async def on_message(message: discord.Message):
    # 忽略機器人自己的訊息
    if message.author == bot.user:
        return
    
    # 確保收到指定ID的訊息
    if message.channel.id != S_CHANNEL_ID:
        return
    
    comm_arr = message.content.split(" ")
    response = await command_handle(comm_arr)
    for v in response:
        await message.channel.send(v)

    # 如果需要同時支持 commands，需顯式處理
    await bot.process_commands(message)

async def command_handle(cmd:list):
    title = str(cmd[0]).upper()
    try:
        if title == 'N':
            try:
                t = int(cmd[3])
            except:
                t = 1
            try:
                memo = str(cmd[4])
            except:
                memo = ""
            msg, id = ba.set_notify(cmd[1], float(cmd[2]), t, memo)
            return [msg, id]
        elif title == 'DN': # 刪除提醒
            id = str(cmd[1])
            msg = ba.del_notify(id)
            return [msg]
        elif title == 'LO': # 開限價單
            s = str(cmd[1])
            # 使用字典映射來設置 d 變數
            mapping = {"l": 1, "s": 2}
            d = mapping.get(cmd[2], 1)  # 如果 cmd[2] 不在字典中，則返回 1
            s_p = float(cmd[3])
            tp = float(cmd[4])
            sl = float(cmd[5])
            msg, id = ba.add_order(s, d, tp, sl, s_p)
            return [msg, id]
        elif title == 'MO': # 開市價單
            s = str(cmd[1])
            # 使用字典映射來設置 d 變數
            mapping = {"l": 1, "s": 2}
            d = mapping.get(cmd[2], 1)  # 如果 cmd[2] 不在字典中，則返回 1
            tp = float(cmd[3])
            sl = float(cmd[4])
            msg, id = ba.add_order(s, d, tp, sl)
            return [msg, id]
        elif title == 'DO': # 刪除訂單
            id = str(cmd[1])
            msg = ba.del_order(id)
            return [msg]
            
    except:
        return ["Error: Invalid Command!"]


# 啟動 Bot
bot.run(TOKEN)