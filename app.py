import datetime
import os

#======python的函數庫==========
import re

#======python的函數庫==========
import tempfile
import time
import traceback

import openai
import requests
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')


def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。' , '')
    return answer


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('hello'))
        mm=Coupang()
        print (mm)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(mm))
        
        # GPT_answer = GPT_response(msg)
        # print(GPT_answer)
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
         line_bot_api.reply_message(event.reply_token, TextSendMessage('小百萬已累累~充電中! 稍後再問我喔~'))
        # print(traceback.format_exc())
        # line_bot_api.reply_message(event.reply_token, TextSendMessage('小百萬已累累~充電中! 稍後再問我喔!'))
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'HI, {name} ! 我是小百萬機器人，很高興你要問我問題')
    line_bot_api.reply_message(event.reply_token, message)
        


def Coupang():
        # 相關變數設定
    Website = "酷澎Coupang" #平台
    MinPrice = 5.03 #上次購入的最低價
    ManyPerDay = 8 #單日用量
    size = 'L'  # 尺寸
    item = '尿布' #品項
    othercritiria = '黏貼' #其他條件
    Keyword = f"{item} {othercritiria} {size}"

    # 瀏覽器
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    content_type = "application/json"
    origin = "https://www.tw.coupang.com"
    header = {
        "User-Agent": user_agent,
        # "Cookie": cookie,
        "Content-Type": content_type,
    }
    datas = {"sort": ["DEFAULT"], "filter": "", "keyword": Keyword, "start": 0, "limit": 60}
    r = requests.post("https://www.tw.coupang.com/search", headers=header, json=datas)
    arrR = r.json()['data']['products']
    # arrR[1]

    dict_Arr =[] 
    max = 60
    for i in range(0,max):
        titleArr = arrR[i]['title'].split(",")
        price = arrR[i]['priceInfo']['price']
        brand = titleArr[0]
        if "成人" not in brand and "大人" not in brand:
            # print(i, brand)
            amount = titleArr[2].strip()
            amount = re.findall(r"\d+", amount)[0]
            unitprice = round(float(price) / float(amount), 4)  # 四捨五入
            dict_Arr.append({'廠牌': brand, '價格':price, '總片數': amount, '單價': unitprice})




    dict_Arr = sorted(dict_Arr, key=lambda x: x['單價'])

    message = f"\n｜百萬現在尺寸: {size} , 用量:{ManyPerDay}片/天｜\n"

    message += f"\n平台：{Website}\n項目：{Keyword}\n目前最低價前三名是\n--------------------------\n"
    for i in range(0,3):

        howlong2use = int(float(dict_Arr[i]["總片數"]) / float(ManyPerDay) )
        message += f'第{i+1}名    單片${dict_Arr[i]["單價"]}\n【{dict_Arr[i]["廠牌"]}】\n${dict_Arr[i]["價格"]} 共{dict_Arr[i]["總片數"]}片（能用:{howlong2use}天）\n--------------------------\n'
    # message += '--------------------------'
    return message
    #print(message)


     
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
