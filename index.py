from bottle import Bottle, run, route, abort, request
import json
import requests
import switch
import timer
import status


app = Bottle()

params = {
    'kadenId': 4,
    'manipulateId': 2,
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
    # heroku側からparamsの受け取り
    # params = request.json.

    kadenId = params['kadenId']
    manipulateId = params['manipulateId']
    timerDatetime = params['timerDatetime']
    timerDatetime = params['timerDatetime']


    #ステータス管理処理
    if manipulateId == 0:
        status = status.Status()
        #resStatus = status.checkStatus(dto.gatKadenId())
        #target_url = ''
        #request.get(target_url, resStatus)

    #ONOFF処理
    elif manipulateId in [1,2]:
        onOff = switch.Switch()           
        onOff.Switching(params)

    #タイマー処理
    elif manipulateId in [3,4]:            
        timer = timer.Timer()            
        timer.timerSetting(params)


if __name__ == "__main__":
    #app.run(host='localhost', port=8080, debug=True, reloader=True)
    index()