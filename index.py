# coding=utf-8
from bottle import Bottle, run, route, abort, request
from crontab import CronTab
import json
import requests
from switch import Switch
from timer import Timer
from status import Status

INT_0 = 0
INT_1 = 1
INT_2 = 2
INT_3 = 3
INT_4 = 4


app = Bottle()

#manipulateIdが0～4以外かのチェック。
def ErrorCheckDeco(func):
    def check(): 
        params = request.json
        manipulateId = int(params['manipulateId'])
        if manipulateId < INT_0 or manipulateId > INT_4:
            msg = "存在しない命令です。"
            target_url = ''
            request.get(target_url, msg)

        else:
            func()

    return check


@app.route('/index', method='POST')
@ErrorCheckDeco
#Main処理
def index():
    status_class = Status()
    switch_class = Switch()
    timer_class = Timer()

    # heroku側からparamsの受け取り
    params = request.json
    kadenId = params['kadenId']
    manipulateId = params['manipulateId']
    timerDatetime = params['timerDatetime']



    #ステータス管理処理
    if int(manipulateId) == INT_0:
        status_reqest = status_class.checkStatus (kadenId)
        
        # heroku.pyへ送信
        target_url = ''
        # request.get(target_url, resStatus)
        print('ステータス　=　' + status_reqest)

    #ONOFF処理
    elif int(manipulateId) in [INT_1, INT_2]:
        onOffData = params
        del onOffData['timerDatetime']
        print(onOffData)
        switch_request = switch_class.Switching(onOffData) #kadenID manipulateIdを渡す
        print('OnOff　=　' + switch_request)

        # heroku.pyへ送信
        target_url = ''
        # request.get(target_url, switch_request)

    #タイマー処理
    elif int(manipulateId) in [INT_3, INT_4]:
        timer_class = Timer()      
        timer_request = timer_class.timerSetting(params) #kadenId manipulateId,timerDatetimeを渡す
        
        # heroku.pyへ送信
        target_url = 'url'
        # request.get(target_url, timer_request)
        print('タイマー　=　' + timer_request)



if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True, reloader=True)