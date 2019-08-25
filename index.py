from bottle import Bottle, run, route, abort, request
import logging
import os
import json
import requests
import io
import datetime
import hashlib
import hmac
import base64
import re

# messaging api関連の変数。

YOUR_CHANNEL_ACCESS_TOKEN = 'ここにアクセストークンを入れる'
YOUR_CHANNEL_SECRET = 'ここにチャンネルシークレットを入れる'

# messaging apiのリプライに使う指定のURL
reply_url = 'https://api.line.me/v2/bot/message/reply'



app = Bottle()



# WEBHOOKで指定したURL(~/callback)にAPIから送られてくるJSONを受ける処理
@app.route('/callback', method='POST')
def callback():


    # -------------------------------------------
    # ここからlineからのアクセスか判別する処理

    # bottleのデフォルトはio.BytesIO型になってしまうため変換
    body = request.body
    text_body = body.read().decode('UTF-8')

    # チャンネルシークレットを秘密鍵に、
    # HMAC-SHA256アルゴリズムでリクエストボディのダイジェスト値取得
    hash = hmac.new(
        YOUR_CHANNEL_SECRET.encode('utf-8'),
        text_body.encode('utf-8'),
        hashlib.sha256).digest()


    # ダイジェスト値をBase64エンコードしてUTF-8でデコード
    signature = base64.b64encode(hash).decode('utf-8')


    # リクエストヘッダーとsignatureの値が正しいか判定し、
    # line以外からのアクセスの場合強制終了させる
    if signature != request.get_header('X-Line-signature'):
        abort(400)
    # -------------------------------------------


    # jsonを受け取る。
    reply_to_line(request.json)

    return {'statusCode': 200, 'body': '{}'}


def reply_to_line(body):


    for event in body['events']:
        responses = []

        # 返信する時に必要となるトークン
        replyToken = event['replyToken']

        type = event['type']

        if type == 'message':

            message = event['message']

            if message['type'] == 'text':

                user_input = message['text']


                # メッセージが規定のものか調べる
                with open('msg.json', 'r') as f:
                    df = json.load(f)

                    for msg in df.values():
                        if user_input == msg:
                            responses.append(
                                LineReplyMessage.mainmenu_response())
                            break
                    else:
                        responses.append(
                            LineReplyMessage.make_text_response('メニュー見たいならメニューって入れろ'))

            else:
                responses.append(
                    LineReplyMessage.make_text_response('テキストで入力しろ'))



        # ボタンによって送られてきたイベントを処理する
        if type == 'postback':

            postback_data = event['postback']['data']


            # 家電を選ぶメニューを表示。これがメインメニュー。
            if postback_data == 'select=manipulate':
                responses.append(LineReplyMessage.kaden_response())


            # 操作する家電を選ぶメニュー。
            elif re.match(r'select=manipulate&kadenId=\d+', postback_data):

                selected_kadenId = postback_data[26:]

                responses.append(LineReplyMessage.make_text_response('家電' + selected_kadenId + '番を操作するよ'))
                responses.append(LineReplyMessage.manipulate_response(selected_kadenId))


            # ステータスを表示する処理
            elif postback_data == 'select=status':
                responses.append(LineReplyMessage.make_text_response('現在の家電の状態を表示する'))

                # status取得し、表示する。


            # 電源をONにする処理
            elif re.match(r'action=on&kadenId=\d+', postback_data):
                manipulated_on_kadenId = postback_data[18:]
                responses.append(LineReplyMessage.make_text_response('家電' + manipulated_on_kadenId + '番の電源を入れるよ'))

                # 選んだ家電の状態確認して電源をONにして、書き換える


            # 電源をOFFにする処理
            elif re.match(r'action=off&kadenId=\d+', postback_data):
                manipulated_off_kadenId = postback_data[19:]
                responses.append(LineReplyMessage.make_text_response('家電' + manipulated_off_kadenId + '番の電源を消すよ'))

                # 選んだ家電の状態確認して電源をOFFにして、書き換える


            # タイマーのモードを設定する画面
            elif re.match(r'select=timer&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[21:]
                responses.append(LineReplyMessage.make_text_response('家電' + selected_timer_kadenId + '番のタイマーを設定するよ'))

                responses.append(LineReplyMessage.timer_response(selected_timer_kadenId))

            # 入タイマーの設定
            elif re.match(r'action=timer&status=from&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[35:]

                responses.append(LineReplyMessage.make_text_response('〜時から点けるタイマーを設定する画面へ飛ばす'))

            # 切タイマーの設定
            elif re.match(r'action=timer&status=to&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[33:]

                responses.append(LineReplyMessage.make_text_response('〜時に消すタイマーを設定する画面へ飛ばす'))

            # 間タイマーの設定
            elif re.match(r'action=timer&status=from_to&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[36:]

                responses.append(LineReplyMessage.make_text_response('〜時から〜時まで点けておくタイマーを設定する画面へ飛ばす'))


        LineReplyMessage.send_reply(replyToken, responses)
        # トークンと配列を元に返信


class LineReplyMessage:


    # メインメニュー
    @staticmethod
    def mainmenu_response():
        return {
            "type": "flex",
            "altText": "mainmenu",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "postback",
                                "label": "家電操作",
                                "data": "select=manipulate"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "状態確認",
                                "data": "select=status"
                            }
                        }
                    ]
                }
            }
        }

    # 操作家電洗濯画面
    @staticmethod
    def kaden_response():
        return {
            "type": "flex",
            "altText": "flexmenu",
            "contents": {
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "家電1"
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "action": {
                                        "type": "postback",
                                        "label": "操作する",
                                        "data": "select=manipulate&kadenId=1"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "家電2"
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "action": {
                                        "type": "postback",
                                        "label": "操作する",
                                        "data": "select=manipulate&kadenId=2"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }


    # 選択した家電の操作画面
    @staticmethod
    def manipulate_response(selected_kadenId):
        return {
            "type": "flex",
            "altText": "manipulate",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "postback",
                                "label": "電源ON",
                                "data": "action=on&kadenId=" + selected_kadenId
                            }
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "postback",
                                "label": "電源OFF",
                                "data": "action=off&kadenId=" + selected_kadenId
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "タイマー",
                                "data": "select=timer&kadenId=" + selected_kadenId
                            }
                        }
                    ]
                }
            }
        }


    # 選択した家電のタイマー設定画面
    @staticmethod
    def timer_response(selected_timer_kadenId):
        return {
            "type": "flex",
            "altText": "timer",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "入",
                                "data": "action=timer&status=from&kadenId=" + selected_timer_kadenId
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "切",
                                "data": "action=timer&status=to&kadenId=" + selected_timer_kadenId
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "間",
                                "data": "action=timer&status=from_to&kadenId=" + selected_timer_kadenId
                            }
                        }
                    ]
                }
            }
        }


    # テキストメッセージ作成
    @staticmethod
    def make_text_response(text):
        return {
            'type': 'text',
            'text': text
        }


    # リプライ定義
    @staticmethod
    def send_reply(replyToken, messages):
        reply = {
            'replyToken': replyToken,
            'messages': messages
        }

        # ヘッダー作成
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(YOUR_CHANNEL_ACCESS_TOKEN)
        }

        # jsonでbotに返す
        requests.post(
            reply_url,
            data=json.dumps(reply),
            headers=headers
        )


if __name__ == "__main__":
    app.run(host='localhost', port=8080)
