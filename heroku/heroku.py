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

__INDEXPY_URL__ = '/index'

app = Bottle()

SHOW_STATUS = 0
POWER_ON = 1
POWER_OFF = 2
TIMER_FROM = 3
TIMER_TO = 4

line_events = {
    'show_main_menu': 'message',
    'show_manipulate_menu': 'postback'
}

show_menu_words = [
    'メニュー',
    'めにゅー',
    'menu',
    'Menu',
    'MENU'
]

COMMON_REPLY_EVENTS = {
    'SHOW_MENU': 0,
    'RETURN_TEXT': 1,
    'SHOW_STATUS': 2,
    'SHOW_SELECT_KADEN_MENU': 3,
    'SHOW_MANIPULATE_KADEN_MENU': 4,
    'SHOW_SET_TIMER_MENU': 5,
}

COMMON_REPLY_EVENTS_FUNCTION = {
    0: 'mainmenu_response',
    1: 'make_text_response',
    2: 'show_status',
    3: 'manipulate_kaden_menu',
    4: 'manipulate_response',
    5: 'timer_response',
}

COMMON_REPLY_EVENTS_WORDS = {
    'NOT_TEXT': 'テキストで入力してよ、ばか',
    'NOT_SHOW_MENU_WORD': 'メニューって入力してね',
}

COMMON_REPLY_EVENTS_TEXT = {
    1: 'の電源を入れるよ',
    2: 'の電源を消すよ',
    3: [
        'から',
        'の電源を点けるよ'
    ],
    4: [
        'に',
        'の電源を消すよ'
    ]
}

REPLY_CLASS_NAME = 'LineReplyMessage.'


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

    # イベントクラス=Lineイベントの種類によって動く
    event = Event()
    event.reply_to_line(request.json)

    return {'statusCode': 200, 'body': '{}'}



class Event:


    def __init__(self):
        kaden_json = open('./tmp/kaden.json')
        self.kaden_info = json.load(kaden_json)

        ini = configparser.ConfigParser()
        ini.read('./tmp/ngrokToHeroku.ini', 'UTF-8')

        # ngrokで指定されるURL
        self.target_url = ini['ngrok']['url'] + __INDEXPY_URL__


    def reply_to_line(self, body):

        # message or postbackで分岐
        for event in body['events']:
            replyToken = event['replyToken']
            type = event['type']

            for key in line_events:
                if type == line_events[key]:
                    responses = eval('self.' + key)(event[type])
                    LineReplyMessage.send_reply(replyToken, responses)


    # messageの場合はこのメソッドへ
    def show_main_menu(self, param):

        message = param
        if message['type'] == 'text':
            if message['text'] in show_menu_words:

                # kaden.jsonの状態確認
                response = self.request_to_index(SHOW_STATUS)

                # response情報を元にkaden.jsonの更新
                self.update_kaden_json(response)

                return self.create_reply_menu(COMMON_REPLY_EVENTS['SHOW_MENU'])
            else:
                return self.create_reply_message(COMMON_REPLY_EVENTS['RETURN_TEXT'], COMMON_REPLY_EVENTS_WORDS['NOT_SHOW_MENU_WORD'])
        else:
            return self.create_reply_message(COMMON_REPLY_EVENTS['RETURN_TEXT'], COMMON_REPLY_EVENTS_WORDS['NOT_TEXT'])


    # postbackの場合はこのメソッドへ
    def show_manipulate_menu(self, param):

        postback_data = param['data']

        # 操作関連
        if re.match(r'select=manipulate.*', postback_data):
            return self.select_kaden_menu(postback_data)

        # 状態確認系
        elif postback_data == 'select=status':
            return self.create_reply_menu(COMMON_REPLY_EVENTS['SHOW_STATUS'], self.kaden_info)

        # ON OFF系
        elif re.match(r'action=o.*', postback_data):
            return self.manipulate_power(postback_data)

        # Timer系
        elif re.match(r'.*timer.*', postback_data):
            return self.manipulate_timer(postback_data, param)


    # 返すテキストを作るメソッド
    def create_reply_message(self, event, *args):

        func = REPLY_CLASS_NAME + COMMON_REPLY_EVENTS_FUNCTION[event]
        res = [eval(func)(args[0])] if len(args) == 1 else [eval(func)(args[0], args[1])]
        return res


    # 返すメニューを作るメソッド
    def create_reply_menu(self, event, *args):

        func = REPLY_CLASS_NAME + COMMON_REPLY_EVENTS_FUNCTION[event]
        if len(args) == 0:
            res = [eval(func)()]

        elif len(args) == 1:
            res = [eval(func)(args[0])]

        elif len(args) == 2:
            res = [eval(func)(args[0], args[1])]

        return res


    # 家電を選ぶメニューを返すメソッド
    def select_kaden_menu(self, postback_data):

        # 操作する家電を選ぶ画面
        if re.match(r'.*kadenId.*', postback_data):
            selected_kadenId = postback_data[26:]
            return self.create_reply_menu(COMMON_REPLY_EVENTS['SHOW_MANIPULATE_KADEN_MENU'], selected_kadenId)

        # 家電を選ぶ画面
        else:
            return self.create_reply_menu(COMMON_REPLY_EVENTS['SHOW_SELECT_KADEN_MENU'], self.kaden_info)


    # 電源関連の操作メソッド
    def manipulate_power(self, postback_data):

        # 電源ON
        if re.match(r'action=on.+', postback_data):
            selected_kadenId = postback_data[18:]
            kadenId = selected_kadenId

            response = self.request_to_index(POWER_ON, kadenId)

            # response情報を元にkaden.jsonの更新
            # self.update_kaden_json(response)

            msg = self.create_manipulate_reply_message(POWER_ON, self.kaden_info[selected_kadenId]['name'])
            return self.create_reply_message(COMMON_REPLY_EVENTS['RETURN_TEXT'], msg)

        # 電源OFF
        elif re.match(r'action=off.+', postback_data):
            selected_kadenId = postback_data[19:]
            kadenId = selected_kadenId

            response = self.request_to_index(POWER_OFF, kadenId)

            # response情報を元にkaden.jsonの更新
            # self.update_kaden_json(response)

            msg = self.create_manipulate_reply_message(POWER_OFF, self.kaden_info[selected_kadenId]['name'])
            return self.create_reply_message(COMMON_REPLY_EVENTS['RETURN_TEXT'], msg)


    # タイマー関連の操作メソッド
    def manipulate_timer(self, postback_data, param):

        # タイマーの種類を選ぶ画面
        if re.match(r'select.*', postback_data):
            selected_kadenId = postback_data[21:]
            return self.create_reply_menu(COMMON_REPLY_EVENTS['SHOW_SET_TIMER_MENU'], self.kaden_info, selected_kadenId)

        # 入タイマーの画面
        elif re.match(r'.*from.*', postback_data):
            selected_kadenId = postback_data[33:]
            kadenId = selected_kadenId
            timer_datetime = param['params']['datetime']
            print("入タイマー : " + timer_datetime)

            response = self.request_to_index(TIMER_FROM, kadenId, timer_datetime)

            # response情報を元にkaden.jsonの更新
            # self.update_kaden_json(response)

            msg = self.create_manipulate_reply_message(TIMER_FROM, timer_datetime, self.kaden_info[selected_kadenId]['name'])
            return self.create_reply_message(COMMON_REPLY_EVENTS['RETURN_TEXT'], msg)

        # 切タイマーの画面
        elif re.match(r'.*to.*', postback_data):
            selected_kadenId = postback_data[31:]
            kadenId = selected_kadenId
            timer_datetime = param['params']['datetime']
            print("切タイマー : " + timer_datetime)

            response = self.request_to_index(TIMER_TO, kadenId, timer_datetime)

            # response情報を元にkaden.jsonの更新
            # self.update_kaden_json(response)

            msg = self.create_manipulate_reply_message(TIMER_TO, timer_datetime, self.kaden_info[selected_kadenId]['name'])
            return self.create_reply_message(COMMON_REPLY_EVENTS['RETURN_TEXT'], msg)


    # 操作のメッセージを作るメソッド
    def create_manipulate_reply_message(self, event, *args):

        if event == 1 or event == 2:
            res = args[0] + COMMON_REPLY_EVENTS_TEXT[event]
        else:
            res = args[0] + COMMON_REPLY_EVENTS_TEXT[event][0] + args[1] + COMMON_REPLY_EVENTS_TEXT[event][1]
        return res


    # ラズパイのindexにrequestを投げる
    ### len(args=1) => ステータス反映 manipulateIdのみ
    ### len(args=2) => 電源系 manipulateId, kadenId
    ### len(args=3) => タイマー系 manipulateId, kadenId, timer_datetime
    def request_to_index(self, *args):

        headers = {'Content-Type': 'application/json'}
        data = {'manipulateId': str(args[0])}
        if len(args) >= 2: data['kadenId'] = str(args[1])
        if len(args) == 3: data['timer_datetime'] = str(args[2])
        responses = requests.post(
            self.target_url ,
            json.dumps(data),
            headers = headers
        )
        return responses


    # index.pyから受け取ったresponsesでkaden.jsonを更新する
    def update_kaden_json(self, responses):

        data = responses.json()

        with open('./tmp/kaden.json', 'w') as f:
            json.dump(data, f, indent=4)



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
                "hero": {
                    "type": "image",
                    "url": "https://www.kajitaku.com/column/wp-content/uploads/2017/12/shutterstock_315007316.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
            "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "Home Appliances Controller",
                    "weight": "bold",
                    "size": "lg"
                }
            ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "color": "#ff7f50",
                        "action": {
                            "type": "postback",
                            "label": "Manipulate",
                            "data": "select=manipulate"
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "color": "#e6e6fa",
                        "action": {
                            "type": "postback",
                            "label": "Show Status",
                            "data": "select=status"
                        }
                    }
                ]
            }
        }
    }

    @staticmethod
    def manipulate_kaden_menu(kaden_info):

        kaden_manipulate_list = []

        for i in range(1, len(kaden_info)+1):

            if kaden_info[str(i)]['name'] == 'エアコン':
                kaden_image = "https://www.kajitaku.com/column/wp-content/uploads/2017/12/shutterstock_315007316.jpg"
            elif kaden_info[str(i)]['name'] == '電気':
                kaden_image = "https://iwiz-chie.c.yimg.jp/im_sigg9r7qhe_vkybPyuDV8E13Ag---x320-y320-exp5m-n1/d/iwiz-chie/que-10143212585"
            else:
                kaden_image = "https://shopping.dmkt-sp.jp/excludes/ds/img/genre/ctg-head-sp03.jpg"

            kaden_manipulate_list.append(
                {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": kaden_image,
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "320:213"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "name:",
                                        "size": "xs",
                                        "margin": "md",
                                        "color": "#8c8c8c",
                                        "flex": 0
                                    },
                                    {
                                    "type": "text",
                                    "text": kaden_info[str(i)]['name'],
                                    "size": "xs",
                                    "margin": "md",
                                    "flex": 0
                                    }
                                ]
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
                                "color": "#00bfff",
                                "action": {
                                    "type": "postback",
                                    "label": "Manipulate",
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
                            "color": "#00bfff",
                            "action": {
                                "type": "postback",
                                "label": "ON",
                                "data": "action=on&kadenId=" + selected_kadenId
                            }
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#c0c0c0",
                            "action": {
                                "type": "postback",
                                "label": "OFF",
                                "data": "action=off&kadenId=" + selected_kadenId
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "postback",
                                "label": "Timer",
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

            if kaden_info[str(i)]['name'] == 'エアコン':
                kaden_image = "https://www.kajitaku.com/column/wp-content/uploads/2017/12/shutterstock_315007316.jpg"
            elif kaden_info[str(i)]['name'] == '電気':
                kaden_image = "https://iwiz-chie.c.yimg.jp/im_sigg9r7qhe_vkybPyuDV8E13Ag---x320-y320-exp5m-n1/d/iwiz-chie/que-10143212585"
            else:
                kaden_image = "https://shopping.dmkt-sp.jp/excludes/ds/img/genre/ctg-head-sp03.jpg"

            if kaden_info[str(i)]['status'] == '1':
                kaden_status = 'ON'
            else:
                kaden_status = 'OFF'


            kaden_status_list.append(
                {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": kaden_image,
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "320:213"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "name:",
                                        "size": "xs",
                                        "margin": "md",
                                        "color": "#8c8c8c",
                                        "flex": 0
                                    },
                                    {
                                    "type": "text",
                                    "text": kaden_info[str(i)]['name'],
                                    "size": "xs",
                                    "margin": "md",
                                    "flex": 0
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "status:",
                                        "size": "xs",
                                        "margin": "md",
                                        "color": "#8c8c8c",
                                        "flex": 0
                                    },
                                    {
                                    "type": "text",
                                    "text": kaden_status,
                                    "size": "xs",
                                    "margin": "md",
                                    "flex": 0
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "signal:",
                                        "size": "xs",
                                        "margin": "md",
                                        "color": "#8c8c8c",
                                        "flex": 0
                                    },
                                    {
                                    "type": "text",
                                    "text": kaden_info[str(i)]['signal'],
                                    "size": "xs",
                                    "margin": "md",
                                    "flex": 0
                                    }
                                ]
                            },
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

    url = request.params.url

    if url != "" :
        print("url:" + url)
        inifile = configparser.ConfigParser()
        inifile.add_section("ngrok")
        inifile.set("ngrok", "url", url)
        with open('./tmp/ngrokToHeroku.ini', 'w') as file:
            inifile.write(file)

    kadenJsonStr = request.params.file
    print("file:" + kadenJsonStr)

    kadenJson = open("./tmp/kaden.json", "w")
    kadenJson.write(kadenJsonStr)

    kadenJson.close()

    print("GetHerokuUrlToHeroku END")

    return {'statusCode': 200, 'body': '{}'}

@app.route('/checkIniFile', method='GET')
def checkIniFile():
    print("GetHerokuUrlToHeroku START")

    body = request.params.url
    print("body:" + body)

    file = open('./tmp/kaden.json', 'r')
    print(file)

    fileini = open('./tmp/ngrokToHeroku.ini', 'r')
    print(fileini)


    return fileini

if __name__ == "__main__":
    port = int(os.getenv('PORT'))
    app.run(host='localhost', port=port, server='gunicorn')
