# coding=utf-8
from bottle import Bottle, run, route, abort, request
from crontab import CronTab
import sys
import json
import requests
import util.Log as Log
import logging
import setNgrokUrlToHeroku
from switch import Switch
from timer import Timer
from status import Status


app = Bottle()

@app.route('/index', method='POST')
#Main処理
def index():

    # heroku側からparamsの受け取り
    params = request.json
    kadenId = params['kadenId']
    manipulateId = int(params['manipulateId'])

    #ステータス管理処理
    if manipulateId == 0:
        status_class = Status()
        logging.info("リクエスト : ステータス管理処理")
        return  status_class.checkStatus ()

    #ONOFF処理
    elif manipulateId in [1, 2]:
        switch_class = Switch()
        logging.info("リクエスト : ONOFF処理")
        return switch_class.switching(params) 

    #タイマー処理
    elif manipulateId in [3, 4]:
        logging.info("リクエスト : タイマー処理")
        timer_class = Timer()     
        return timer_class.timerSetting(params)

if __name__ == "__main__":
    # ログ出力の初期化
    Log.initLog()
    logging.info("起動 : SmartController ")

    # Ngrokの起動⇒Herokuへの送信
    if setNgrokUrlToHeroku.execNgrok() == False:
        print("エラー : Ngrokの起動に失敗したため終了します。NgrokWebのステータスに何か残ってないか見てみてね")
        sys.exit(-1)

    logging.info("Webサーバー待ち受け開始")
    app.run(host='localhost', port=8080)