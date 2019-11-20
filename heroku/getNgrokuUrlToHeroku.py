
from bottle import Bottle, run, route, abort, request

import configparser
import os

app = Bottle()

# heroku config.set 環境変数名="値" でherokuの環境変数を指定して、os.environで取れる。
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

@app.route('/getNgrokuUrlToHeroku', method='POST')
def GetNgrokuUrlToHeroku():

    body = request.body
    text_body = body.read().decode('UTF-8')
    print(text_body)

    inifile = configparser.ConfigParser()
    inifile.read("./settings/ngrokToHeroku.ini")
    inifile.set("ngrok", "url", text_body)

    return {'statusCode': 200, 'body': '{}'}

