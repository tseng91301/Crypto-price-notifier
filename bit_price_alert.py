import json
from queue import LifoQueue

import requests
import threading
import time
import random
import string

notify_queue = LifoQueue()
notify_list:list = json.loads(open("run/bit_price_alert.json", "r").read())
avail_symbol = json.loads(open("conf/available_product.json", "r").read())

PRICE_ALERT = 0
LIMIT_ORDER_OPEN = 2
LIMIT_ORDER_STOP = 3
LIMIT_ORDER_STOP_LOSS = 4
LIMIT_ORDER_TAKE_PROFIT = 5

def save():
    open("run/bit_price_alert.json", "w").write(json.dumps(notify_list))

def generate_random_string(length=20):
    # 定義字母和數字的組合
    characters = string.ascii_letters + string.digits
    # 隨機選擇字符並組合成字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    duplicate = False
    for item in notify_list:
        try:
            if random_string in item["id"]:
                duplicate = True
                break
        except:
            continue
    if duplicate:
        return generate_random_string()
    else:
        return random_string

def set_notify(symbol:str, price:float, times:int=1, memo:str=""):
    symbol = symbol.upper()
    if symbol not in avail_symbol:
        return f"Symbol Not Fount at Bitget"
    now_price = float(get_price(symbol))
    id = generate_random_string()
    notify_list.append({"s": symbol, "p": price, "t": times, "sp": now_price, "m": memo, "id": id, "type": PRICE_ALERT})
    save()
    return f"Notify set successfully! [{symbol} at {price} for {times} time(s)], notify ID displays below:", id

def del_notify(id:str):
    global notify_list
    try:
        notify_list = [v for v in notify_list if v["id"] != id]
        save()
        return f"Notify deleted successfully [id = {id}]"
    except:
        return f"Invalid ID! [id = {id}]"

def del_order(id: str):
    global notify_list
    found = False
    for i, v in enumerate(notify_list):
        try:
            if v["id"] == id:
                del notify_list[i]
                found = True
                pass
            elif v["trigger_id"] == id:
                del notify_list[i]
                found = True
                pass
        except:
            pass
        pass
    save()
    if found:
        return f"Order deleted successfully [id = {id}]"
    else:
        return f"Invalid ID! [id = {id}]"
    
def add_order(symbol: str, direction: int, tp: int, sl: int, start_price: int = -1):
    global notify_list
    now_price = get_price(symbol)
    id_s = generate_random_string()
    id_o = generate_random_string()
    if direction == 1: # 多單
        open_msg = "Limit-price LONG Order open."
        d_m = "LONG"
    else:
        open_msg = "Limit-price SHORT Order open."
        d_m = "SHORT"
    if start_price == -1:
        start_price = now_price
        on = 1
        pass
    else:
        on = 0
        notify_list.append({"s": symbol, "p": start_price, "t": 1, "sp": now_price, "m": open_msg, "id": id_o, "type": LIMIT_ORDER_OPEN, "trigger_id": id_s})
    notify_list.append({"s": symbol, "p": tp, "t": 1, "sp": now_price, "m": f"Take Profit, ID: {id_o}", "id": id_s, "type": LIMIT_ORDER_STOP, "t1": LIMIT_ORDER_TAKE_PROFIT, "on": on})
    notify_list.append({"s": symbol, "p": sl, "t": 1, "sp": now_price, "m": f"Stop Loss, ID: {id_o}", "id": id_s, "type": LIMIT_ORDER_STOP, "t1": LIMIT_ORDER_STOP_LOSS, "on": on})
    save()
    return f"Order set successfully [{symbol} {d_m} order at {start_price}, tp={tp}, sl={sl}], order ID displays below:", id_s
    

def get_price(symbol:str):
    url = "https://api.bitget.com/api/v2/mix/market/ticker"
    params = {
        "productType": "USDT-FUTURES",
        "symbol": symbol
    }
    response = requests.get(url, params=params)
    try:
        pri = response.json()["data"][0]["lastPr"]
        return float(pri)
    except:
        return 0

def notify_service():
    global notify_list
    while True:
        notify_list = [v for v in notify_list if v["t"] > 0] # 更新通知列表，將通知次數用完的去除
        for i, v in enumerate(notify_list):
            pri = get_price(v["s"])
            # print(f"{pri}, {v['p']}, {v['sp']}")
            try:
                type = int(v["type"])
                trigger = (pri <= v["p"] <= v["sp"] or pri >= v["p"] >= v["sp"])
                if type == PRICE_ALERT:
                    if trigger:
                        if pri >= v["p"]: # 漲破
                            notify_queue.put({"s": v["s"], "p": v["p"], "d": "u", "m": v["m"]}) # d 指方向，漲破: u；跌破: d。 s: symbol, p: price
                        else: # 跌破
                            notify_queue.put({"s": v["s"], "p": v["p"], "d": "d", "m": v["m"]})
                        notify_list[i]["sp"] = pri
                        notify_list[i]["t"] -= 1
                        save()
                    else:
                        continue
                elif type == LIMIT_ORDER_OPEN:
                    if trigger:
                        notify = False
                        for orders in notify_list:
                            if (orders["type"]) == LIMIT_ORDER_STOP and orders["id"] == v["trigger_id"]:
                                orders["on"] = 1
                                notify = True
                                pass
                            pass
                        if notify:
                            notify_queue.put({"s": v["s"], "p": v["p"], "d": "-", "m": v["m"]})
                            notify_list[i]["t"] -= 1
                            save()
                elif type == LIMIT_ORDER_STOP:
                    if trigger and int(v["on"] == 1):
                        notify_queue.put({"s": v["s"], "p": v["p"], "d": "-", "m": v["m"]})
                        del_notify(v["id"])
                        save()
                            
            except:
                continue
        time.sleep(0.15)

notify_thread = threading.Thread(target=notify_service)
notify_thread.start()

