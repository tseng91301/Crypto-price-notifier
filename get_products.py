import requests
import json

url = "https://api.bitget.com/api/v2/mix/market/tickers"
params = {
    "productType": "USDT-FUTURES",
}

response = requests.get(url, params=params)
data = response.json()

if data['code'] == "00000":
    avail_product = []
    for v in data["data"]:
        avail_product.append(v["symbol"])
    open("conf/available_product.json", "w").write(json.dumps(avail_product))
    print("Stored successfully!")
else:
    print("Failed to get contents!")
