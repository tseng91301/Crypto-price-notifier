import json

file_name = "run/bit_price_alert.json"
data = json.loads(open(file_name, "r").read())

# 為所有沒有 "type" 鍵的字典添加 "type"
for item in data:
    if "type" not in item:
        item["type"] = 0  # 可以根據需要設置默認值

open(file_name, "w").write(json.dumps(data))