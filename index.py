from bottle import Bottle, run, route, abort, request
import os, json, requests, io
import hashlib, hmac, base64
import status


# messaging api関連の変数。

YOUR_CHANNEL_ACCESS_TOKEN = 'ここにアクセストークンを入れる'
YOUR_CHANNEL_SECRET = 'ここにチャンネルシークレットを入れる'

# messaging apiのリプライに使う指定のURL
reply_url = 'https://api.line.me/v2/bot/message/reply'
# messaging apiのプッシュに使う指定のURL
push_url = 'https://api.line.me/v2/bot/message/push'


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
                responses.append(LineReplyMessage.make_text_response('ここに返すメッセージを入れる'))

                # ボタン返すテスト「操作」or「確認」でテキストを返すボタンを返す
                if message['text'] == '操作':
                    responses.append(LineReplyMessage.make_confirm_response('はい', 'いいえ', '家電操作する？'))
                elif message['text'] == '確認':
                    responses.append(LineReplyMessage.make_confirm_response('はい', 'いいえ', '状態確認する？'))

            else:
                responses.append(LineReplyMessage.make_text_response('規定のテキストを入力してくれ。'))
                # テキストでの返信内容を配列に追加

        LineReplyMessage.send_reply(replyToken, responses)
        # トークンと配列を元に返信


class LineReplyMessage:


    # 確認ボタン作成。
    @staticmethod
    def make_confirm_response(text1, text2, text3):
        return {
            'type': 'template',
            'altText': 'this is a confirm template',
            'template': {
                'type': 'confirm',
                'actions': [
                    {
                        'type': 'message',
                        'label': text1,
                        'text': text1
                    },
                    {
                        'type': 'message',
                        'label': text2,
                        'text': text2
                    }
                ],
                'text': text3
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
