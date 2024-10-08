import os

import openai
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import coupang

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
# openai.api_key = os.getenv('OPENAI_API_KEY')

mm = coupang.Coupang()
line_bot_api.push_message(event.reply_token, TextSendMessage(mm))


def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500
    )
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。', '')
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
    if '尿布' in msg:
        try:
            mm = coupang.Coupang()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(mm))
            # GPT_answer = GPT_response(msg)
            # print(GPT_answer)
            # line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
        except Exception:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage('小百萬已累累~充電中! 稍後再問我喔~')
            )
        # print(traceback.format_exc())
        # line_bot_api.reply_message(event.reply_token, TextSendMessage('小百萬已累累~充電中! 稍後再問我喔!'))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('目前關鍵字只支援"尿布"'))


# @handler.add(PostbackEvent)
# def handle_message(event):
#     print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'HI, {name} ! 我是小百萬機器人，很高興你要問我問題')
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
