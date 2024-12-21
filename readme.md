## 首次運行配置
1. 創建`./conf` 目錄(資料夾)，並在裡面新增 `api_settings.json` 和 `available_product.json`

`api_settings.json`: 
```json
{
    "token": <Your Discord bot token: string>,
    "notify_channel_id": <channel id to get notification: int>,
    "settings_msg_channel_id": <channel id to set notification: int>
}
```
* 關於如何獲取上面需要的的內容，可以參考 [Appendix](#設定您的discord-bot)

`available_product.json`:
```json
[]
```

1. 安裝Python所需函式庫

```shell
pip install discord
```

3. 更改執行檔權限 (Linux 版本適用)

```shell
chmod 755 *.sh
```

4. 開啟伺服器
   1. 打開cmd 或 shell， `cd` 到此目錄下
   2. 執行`python get_products.py` 獲取所有合約交易對
   3. 執行`python main.py` 打開伺服器 (**此執行程序須一直保持開啟，否則會出現錯誤**)

## 功能列表
### 設定價格提醒
Command: `N <symbol: string> <Notify price: float> <notify times: int> <notify memo: string>`

### 刪除價格提醒
Command: `DN <id: string>`

### 設定一個市價訂單
Command: `MO <symbol: string> <direction: char> <Take profit price: float> <Stop loss price: float>`
* direction: l: 多單, s: 空單

### 設定一個限價訂單
Command: `LO <symbol: string> <direction: char> <Trigger price> <Take profit price: float> <Stop loss price: float>`
* direction: l: 多單, s: 空單
* Trigger price: 買入訂單的價格

### 刪除訂單(限價、市價通用)
Command: `DO <id: string>`

### 備註
* `id` 是在創建訂單或提醒之後會生成在回覆的一個20位英數字混和字串，可直接複製用於刪除訂單或提醒

## Appendix

### 設定您的Discord bot
*可以參考 https://hackmd.io/@smallshawn95/python_discord_bot_base 的教學 (看到 三、Discord Bot 創建)*

1. 創建一個伺服器，並設定至少2個文字聊天室(一個接收通知，另一個用來設置)
2. 在電腦版的Discord(您創建的伺服器)應該會有"文字頻道"，裡面會有您新增的兩個文字聊天室。
3. 對著聊天室名稱點擊右鍵，點「複製連結」
4. 貼出來後複製這個url的最後一串數字，放到`api_settings.json`內(分別有通知和設置兩個聊天室ID)