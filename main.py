from flask import Flask, request, abort
import twder
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)

msg_tip = """
歡迎使用 Line 匯率查詢機器人
---------------------------------
使用教學：
1.查詢 幣別 > 回傳該幣別匯率
2.清單      > 回傳幣別清單
---------------------------------
例：查詢 美金
即回傳新台幣兌換美金匯率
"""

# Line Bot驗證
line_bot_api = LineBotApi("Eqzcj6SDxRTFSDv7l8ceI09j830Pg2571ePo7ZLcLszblj9b6Mqa8lA0YsLsHi+nQRIUjnqCkIqrejnIWVpQfuhGn5w3a4Aa3PKxFR5WsRtjo3XemuHy9hBKpUXDuivKAQs2J+ZtKnjdZNBV3KcLVgdB04t89/1O/w1cDnyilFU=")    
handler = WebhookHandler("88ea471388aeec4f30eaae663e0bfd73")
# Push訊息到指定的UserID中
#line_bot_api.push_message("您的Line Bot UserID", TextSendMessage(text="歡迎使用Line 匯率查詢機器人"))

# 台灣銀行可換匯幣別清單
cur_list = {}
cur_ch_list = {}
twch = twder.currency_name_dict()
cur_list_str = ''
for i in iter(twch):
    cur_list[i] = twch[i].split()[0]
    cur_ch_list[twch[i].split()[0]] = i
    cur_list_str = cur_list_str + i + twch[i].split()[0] + '\n'

# 查詢輸入幣別即時匯率(可輸入中文或英文)
def twder_currency(query_cur):
    # 輸入中文時須轉換成英文
    if query_cur in cur_list:
        pass
    elif query_cur in cur_ch_list:
        query_cur = cur_ch_list[query_cur]
    return twder.now(query_cur)


# 設定Line Bot回覆訊息
def createReplyMessge(query_cur):
    try:
        replyCheckMessage = (f"您查詢的幣別是：{query_cur}\n時間：%s\n現金買入：%s\n現金賣出：%s\n即期買入：%s\n即期賣出：%s"%twder_currency(query_cur))
    except:
        replyCheckMessage = "查無資料，無此幣別!!\n%s"%msg_tip
    return replyCheckMessage

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback(request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def line_reply(event, msg_text):
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=msg_text, type="text")
        )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if "查詢" in event.message.text or "Query" in event.message.text:
        try:
            query_cur = event.message.text.split()[1]
            # 格式正確,查詢資料
            line_reply(event, createReplyMessge(query_cur))
        except:
            line_reply(event, "輸入錯誤!!\n%s"%msg_tip)
    elif "清單" in event.message.text or "List" in event.message.text:
        line_reply(event, cur_list_str)
    else: # 輸入其他文字則回傳Tip
        line_reply(event, "輸入錯誤!!\n%s"%msg_tip)
            
if __name__ == "__main__":
    app.run(host='0.0.0.0')

