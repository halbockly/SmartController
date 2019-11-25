from bottle import Bottle, run, route, abort, request
import json
import requests


app = Bottle()

params = {
    'kadenId': 5,
    'manipulateId': 6,
    'timerDatetime': '2019-09-08T11:00'
}

class paramaters():
    def __init__(self, kadenId, manipulateId, timerDatetime):
        self.kadenId = kadenId
        self.manipulateId = manipulateId
        self.timerDatetime = timerDatetime

    def gatKadenId(self):
        return self.kadenId

    def gatManipulateId(self):
        return self.manipulateId

    def gatTimerDatetime(self):
        return self.timerDatetime

#manipulateIdが0～4以外かのチェック。
def ErrorCheckDeco(func):
    def check():
        par = paramaters(params["kadenId"], params["manipulateId"], params["timerDatetime"])
        if par.gatManipulateId() < 0 or par.gatManipulateId() > 4:
            print("存在しない命令です。")

        else:
            func()

    return check





#main処理
#@app.route('/test', method='POST')
@ErrorCheckDeco
def index():

    # heroku側からparamsの受け取り
    # params = request.json.



    par = paramaters(params["kadenId"], params["manipulateId"], params["timerDatetime"])

    #command分岐
    if par.gatManipulateId() == 0:from bottle import Bottle, run, route, abort, request
import json
import requests
import indexDto
import switch
import timer
import status


app = Bottle()

params = {
    'kadenId': 4,
    'manipulateId': 2,
    'timerDatetime': '2019-09-08T11:00'
}


def ErrorCheckDeco(func):                           #manipulateIdが0～4以外かのチェック。
    def check():
        dto = indexDto.ParamsDto()
        dto.setParams(params["kadenId"], params["manipulateId"], params["timerDatetime"])

        if dto.gatManipulateId() < 0 or dto.gatManipulateId() > 4:
            print("存在しない命令です。")

        else:
            func()

    return check


@app.route('/test', method='POST')
@ErrorCheckDeco
def index():                                        #Main処理

    # heroku側からparamsの受け取り
    # params = request.json.

    dto = indexDto.ParamsDto()
    dto.setParams(params["kadenId"], params["manipulateId"], params["timerDatetime"])

    #command分岐
    if dto.gatManipulateId() == 0:                  #ステータス管理処理
        status = status.Status()
        resStatus = status.checkStatus(dto.gatKadenId())
        target_url = ''
        request.get(target_url, resStatus)

    elif dto.gatManipulateId() in [1,2]:            #ONOFF処理
        onOff = switch.Switch()           
        onOff.Switching(params)                     #スイッチOnOff

    elif dto.gatManipulateId() in [3,4]:            #タイマー処理
        timer = timer.Timer()            
        timer.timerSetting(params)                  #タイマー予約


if __name__ == "__main__":
    #app.run(host='localhost', port=8080, debug=True, reloader=True)
    index()