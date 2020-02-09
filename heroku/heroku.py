from bottle import Bottle, run, route, abort, request
import os
import json
import requests
import datetime
import hashlib
import hmac
import base64
import re
import configparser

# heroku config.set 環境変数名="値" でherokuの環境変数を指定して、os.environで取れる。
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

# line messaging api指定のリプライ、プッシュURL
reply_url = 'https://api.line.me/v2/bot/message/reply'
push_url = 'https://api.line.me/v2/bot/message/push'

ini = configparser.ConfigParser()
ini.read('tmp/ngrokToHeroku.ini', 'UTF-8')


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


    # 家電名、状態、数などを取得
    # kaden.jsonは同ディレクトリ？
    kaden_json = open('kaden.json')
    kaden_info = json.load(kaden_json)


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
                # msg.jsonに規定メッセージ書く？
                with open('msg.json', 'r') as f:
                    df = json.load(f)

                    for msg in df.values():
                        if user_input == msg:

                            # それぞれの家電の状態確認してjsonに反映するために、
                            # ラズパイのindex.pyにリクエスト送って、jsonを更新

                            # ngrokで指定されるURL
                            target_url = ini['ngrok']['url']
                            headers = {'Content-Type': 'application/json'}

                            # 状態確認して状態のjson更新する。manipulateId=0→ステータス確認
                            requests.get(
                                target_url,
                                params = {
                                    'manipulateId': '0'
                                },
                                headers = headers
                            )

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
                responses.append(LineReplyMessage.kaden_response(kaden_info))


            # 操作する家電を選ぶメニュー。
            elif re.match(r'select=manipulate&kadenId=\d+', postback_data):

                selected_kadenId = postback_data[26:]

                # 操作する家電のIDをテキストで返し、操作画面を返す。
                responses.append(LineReplyMessage.make_text_response(kaden_info[selected_kadenId]['name'] + 'を操作するよ'))
                responses.append(LineReplyMessage.manipulate_response(selected_kadenId))


            # ステータスを表示する処理
            elif postback_data == 'select=status':
                # responses.append(LineReplyMessage.make_text_response('現在の家電の状態を表示する'))
                responses.append(LineReplyMessage.show_status(kaden_info))


            # 電源をONにする処理
            elif re.match(r'action=on&kadenId=\d+', postback_data):
                manipulated_on_kadenId = postback_data[18:]
                responses.append(LineReplyMessage.make_text_response(kaden_info[manipulated_on_kadenId]['name'] + 'の電源を入れるよ'))

                # 選んだ家電の状態確認して電源をONにして、書き換える

                # kadenId　→　操作対象
                # manipulateId → 1=ON, 2=OFF
                kadenId = manipulated_on_kadenId

                # index.pyが受け取るURL
                target_url = ini['ngrok']['url']
                headers = {
                    'Content-Type': 'application/json'
                }

                # getでindex.pyに送信
                requests.get(
                    target_url,
                    params = {
                        'kadenId': str(kadenId),
                        'manipulateId': '1'
                    },
                    headers = headers
                )


            # 電源をOFFにする処理
            elif re.match(r'action=off&kadenId=\d+', postback_data):
                manipulated_off_kadenId = postback_data[19:]
                responses.append(LineReplyMessage.make_text_response(kaden_info[manipulated_off_kadenId]['name'] + 'の電源を消すよ'))


                # kadenId　→　操作対象
                # manipulateId → 1=ON, 2=OFF
                kadenId = manipulated_off_kadenId

                # index.pyが受け取るURL
                target_url = ini['ngrok']['url']
                headers = {'Content-Type': 'application/json'}

                # getでindex.pyに送信
                requests.get(
                    target_url,
                    params = {
                        'kadenId': str(kadenId),
                        'manipulateId': '2'
                    },
                    headers = headers
                )


            # タイマーのモードを設定する画面
            elif re.match(r'select=timer&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[21:]

                # タイマー設定画面を返す。
                responses.append(LineReplyMessage.timer_response(kaden_info, selected_timer_kadenId))


            # 入タイマーの設定
            elif re.match(r'action=timer&status=from&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[33:]
                postback_params = event['postback']['params']['datetime']
                responses.append(LineReplyMessage.make_text_response(postback_params + 'から' + kaden_info[selected_timer_kadenId]['name'] + 'を点けるよ'))

                # 入力した時間と選んだ家電IDをindexに渡す。
                # 時刻は「2019-09-08T11:00」といった形式で返るためそのまま渡す。詳しい動作はテストボット参照
                # timer_manipulateIdは、1=タイマーON, 2=タイマーOFF
                kadenId = selected_timer_kadenId
                timer_datetime = postback_params

                target_url = ini['ngrok']['url']
                headers = {'Content-Type': 'application/json'}

                requests.get(
                    target_url,
                    params = {
                        'kadenId': str(kadenId),
                        'timer_datetime': str(timer_datetime),
                        'manipulateId': '3',
                    },
                    headers = headers
                )

            # 切タイマーの設定
            elif re.match(r'action=timer&status=to&kadenId=\d+', postback_data):
                selected_timer_kadenId = postback_data[31:]
                postback_params = event['postback']['params']['datetime']
                responses.append(LineReplyMessage.make_text_response(postback_params + 'まで' + kaden_info[selected_timer_kadenId]['name'] + 'を点けるよ'))

                # 入力した時間と選んだ家電IDをindexに渡す。
                # 時刻は「2019-09-08T11:00」といった形式で返るためそのまま渡す。詳しい動作はテストボット参照
                kadenId = selected_timer_kadenId
                timer_datetime = postback_params

                target_url = ini['ngrok']['url']
                headers = {'Content-Type': 'application/json'}

                requests.get(
                    target_url,
                    params = {
                        'kadenId': str(kadenId),
                        'timer_datetime': str(timer_datetime),
                        'manipulateId': '4',
                    },
                    headers = headers
                )


        LineReplyMessage.send_reply(replyToken, responses)
        # トークンと配列を元に返信


class LineReplyMessage:

    # lineのリプライ先URL
    ReplyEndpoint = reply_url

    # タイマーメニュー
    @staticmethod
    def timer_response(kaden_info, selected_timer_kadenId):
        return {
            'type': 'template',
            'altText': 'this is a timer test',
            'template': {
                'type': 'buttons',
                'actions': [
                    {
                        "type":"datetimepicker",
                        "label":"入",
                        "data":"action=timer&status=from&kadenId=" + selected_timer_kadenId,
                        "mode":"datetime"
                    },
                    {
                        "type":"datetimepicker",
                        "label":"切",
                        "data":"action=timer&status=to&kadenId=" + selected_timer_kadenId,
                        "mode":"datetime"
                    }
                ],
                'text': kaden_info[selected_timer_kadenId]['name'] + 'のタイマーを設定'
            }
        }

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

    # 操作家電選択画面
    @staticmethod
    def kaden_response(kaden_info):

        kaden_manipulate_list = []
        for i in range(1, len(kaden_info)+1):
            kaden_manipulate_list.append(
                {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": kaden_info[str(i)]['name']
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
                                    "data": "select=manipulate&kadenId=" + str(i)
                                }
                            }
                        ]
                    }
                }
            )

        return {
            "type": "flex",
            "altText": "flexmenu",
            "contents": {
                "type": "carousel",
                "contents": kaden_manipulate_list
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


    @staticmethod
    def show_status(kaden_info):

        kaden_status_list = []
        for i in range(1, len(kaden_info)+1):

            if kaden_info[str(i)]['status'] == '1':
                kaden_status = '電源ON'
            else:
                kaden_status = '電源OFF'

            kaden_status_list.append(
                {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "家電名 : " + kaden_info[str(i)]['name']
                            }
                        ]
                    },
                    "body": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "状態 : " + kaden_status
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "信号 : " + kaden_info[str(i)]['signal']
                            }
                        ]
                    }
                }
            )

        return {
            "type": "flex",
            "altText": "show_status",
            "contents": {
                "type": "carousel",
                "contents": kaden_status_list
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

# ngroku Urlの受け取り（別ファイル化がうまくいかなかったので間借りさせてもらいました。
@app.route('/getNgrokuUrlToHeroku', method='POST')
def getNgrokuUrlToHeroku():
    print("GetHerokuUrlToHeroku START")

    body = request.params.url
    print("body:" + body)

    inifile = configparser.ConfigParser()

    inifile.add_section("ngrok")
    inifile.set("ngrok", "url", body)

    with open('./tmp/ngrokToHeroku.ini', 'w') as file:
        inifile.write(file)

    inifile.close()

    kadenJsonStr = request.params.file
    print("file:" + kadenJsonStr)

    kadenJson = open("./tmp/kaden.json", "w")
    kadenJson.write(kadenJsonStr)

    kadenJson.close()

    print("GetHerokuUrlToHeroku END")

    return {'statusCode': 200, 'body': '{}'}


if __name__ == "__main__":
    port = int(os.getenv('PORT'))
    app.run(host='localhost', port=port, server='gunicorn')
