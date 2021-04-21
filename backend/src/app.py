from flask import Flask, request, abort
from token_key import YOUR_CHANNEL_SECRET, YOUR_CHANNEL_ACCESS_TOKEN
from library.quiz import Quiz


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage, TemplateSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction
)

app = Flask(__name__)
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


quiz = Quiz()


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    app.logger.info(user_id)
    if event.message.text == "選択クイズ":
        send_messages = quiz.make_quiz(user_id, select=True)
        line_bot_api.reply_message(
            event.reply_token,
            send_messages
        )
    elif event.message.text == "記述クイズ":
        send_messages = quiz.make_quiz(user_id=user_id)
        line_bot_api.reply_message(
            event.reply_token,
            send_messages
        )
    else:
        send_messages = quiz.get_answer(user_id, event.message.text)
        app.logger.debug(send_messages)
        if send_messages:
            line_bot_api.reply_message(
                event.reply_token,
                send_messages
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="「選択クイズ」と打つと選択形式のクイズをだすよ！\n「記述クイズ」と打つと自由記述形式のクイズをだすよ！"))


@handler.add(PostbackEvent)
def on_postback(event):
    data = event.postback.data
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=data))


if __name__ == "__main__":
    app.run()
