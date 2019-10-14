
# とりあえずのサンプルソース（動作確認済み
import configparser

@app.route('/getNgrokuUrlToHeroku', method='POST')
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