
from bottle import Bottle, run, route, abort, request
# とりあえずのサンプルソース（動作確認済み
import configparser

app = Bottle()

@app.route('/getNgrokuUrlToHeroku', method='POST')
def GetNgrokuUrlToHeroku():

    body = request.body
    text_body = body.read().decode('UTF-8')
    print(text_body)

    inifile = configparser.ConfigParser()
    inifile.read("./settings/ngrokToHeroku.ini")
    inifile.set("ngrok", "url", text_body)

    return {'statusCode': 200, 'body': '{}'}

