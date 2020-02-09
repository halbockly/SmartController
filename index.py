from bottle import Bottle, run, route, abort, request
from crontab import CronTab
import json
import requests
from switch import Switch
from timer import Timer
from status import Status


app = Bottle()

# 辞書型
params = {
    'kadenId': 4,
    'manipulateId': 1,
    'timerDatetime': '2019-09-08T11:00'
}




#manipulateIdが0～4以外かのチェック。
def ErrorCheckDeco(func): 
    def check():
        manipulateId = params['manipulateId']
        if manipulateId < 0 or manipulateId > 4:
            print("存在しない命令です。")

        else:
            func()

    return check


@app.route('/test', method='POST')
@ErrorCheckDeco
#Main処理
def index():
    status_class = Status()
    switch_class = Switch()
    timer_class = Timer()

    # heroku側からparamsの受け取り
    # params = request.json
    params = {
    'kadenId': 4,
    'manipulateId': 1,
    'timerDatetime': '2019-09-08T11:00'
}

    kadenId = params['kadenId']
    manipulateId = params['manipulateId']
    timerDatetime = params['timerDatetime']


    #ステータス管理処理
    if manipulateId == 0:
        jsonparams(params, manipulateId)
        resStatus = status_class.checkStatus (kadenId)
        target_url = ''
        request.get(target_url, resStatus)

    #ON処理
    elif manipulateId == 1:
        params = {
                    'kadenId': 1,
                    'manipulateId': 1
                }
        jsonparams(params, manipulateId)
        switch_class.Switching(params) #kadenID manipulateIdを渡す

    #OFF処理
    elif manipulateId == 2:
        params = {
                    'kadenId': 1,
                    'manipulateId': 2
                }
        jsonparams(params, manipulateId)          
        switch_class.Switching(params) #kadenID manipulateIdを渡す

    #タイマー処理
    elif manipulateId == 3:
        timer_class = Timer()
        params = {
                    'kadenId': 1,
                    'manipulateId': 3,
                    'timerDatetime': '2019-09-08T11:00'
                }           
        timer_class.timerSetting(params) #kadenId manipulateId,timerDatetime

    elif manipulateId == 4:
        params = {
                    'kadenId': 1,
                    'manipulateId': 4,
                    'timerDatetime': '2019-09-08T11:00'
                }           
    timer_class.timerSetting(params) #kadenId manipulateId,timerDatetime
    
def jsonparams(params, manipulateId):
    for jsonData in params.items():
        if manipulateId == 0:
            print(jsonData)
            break




    

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True, reloader=True)