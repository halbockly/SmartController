# -*- coding: utf-8 -*-

from bottle import Bottle, run, route, abort, request
# とりあえずのサンプルソース（動作確認済み
import configparser
import subprocess
import time
import requests

app = Bottle()


@app.route('/getNgrokuUrlToHeroku', method='POST')
def GetNgrokuUrlToHeroku():
    print("GetHerokuUrlToHeroku START")

    body = request.params.url
    print("body:" + body)

    inifile = configparser.ConfigParser()
    inifile.read("./settings/ngrokToHeroku.ini")
    inifile.set("ngrok", "url", body)

    kadenJsonStr = request.params.file
    print("file:" + kadenJsonStr)

    kadenJson = open("./settings/kaden.json", "w")
    kadenJson.write(kadenJsonStr)

    kadenJson.close()

    print("GetHerokuUrlToHeroku END")

    return {'statusCode': 200, 'body': '{}'}


if __name__ == "__main__":
    port = 80
    app.run(host='localhost', port=port)