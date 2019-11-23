from bottle import Bottle, run, route, abort, request
import json
import requests


app = Bottle()

params = {
    'kadenId': 1,
    'manipulateId': 0,
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
    if par.gatManipulateId() == 0:
        print("家電状況の取得をします。")
        target_url = ''
        request.get(target_url, "sutats.pyから帰ってきたjson")

    elif par.gatManipulateId() == 1:
        print("電源ON")

    elif par.gatManipulateId() == 2:
        print("電源OFF")

    elif par.gatManipulateId() == 3:
        print(par.gatTimerDatetime() + "タイマーON")

    elif par.gatManipulateId() == 4:
        print(par.gatTimerDatetime() + "タイマーOFF")





if __name__ == "__main__":
    #app.run(host='localhost', port=8080, debug=True, reloader=True)
    index()
