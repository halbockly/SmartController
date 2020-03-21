from bottle import Bottle, run, route, abort, request
import sys
import json
import requests
import logging


from _switch import Switch
from _status import Status
from _timer import Timer
import util.log as Log
import setNgrokUrlToHeroku

app = Bottle()

exec_settings = {
    "exec_status": ["0"],
    "exec_switch": ["1", "2"],
    "exec_timer": ["3", "4"]
}


@app.route('/index', method='POST')
def index():
    logging.info("LINE API⇒Herokuからのリクエスト")

    msg = None
    params = request.json

    try:
        for key in exec_settings:
            if params["manipulateId"] in exec_settings[key]:
                msg = eval(key)(params)

        result = {
            "status": 200,
            "message": msg
        }

    except Exception as e:
        result = {
            "status": 500,
            "message": e
        }

    logging.info("LINE API⇒Herokuへ返信" + result)
    return json.dumps(result, ensure_ascii=False)


def exec_status(params):
    logging.info("リクエスト＝ステータス取得")
    st = Status(params)
    status = st.get_current_status()
    return {"kadenId": st.kaden_id, "status": status}


def exec_switch(params):
    logging.info("リクエスト＝スイッチ")
    sw = Switch(params)
    return sw.switching()


def exec_timer(params):
    logging.info("リクエスト＝タイマー")
    ti = Timer()
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
    app.run(host='localhost', port=8080, debug=True, reloader=True) #reloader=falseでないととログ2回出ちゃうんだけど
                                                                     #falseじゃだめ？
    logging.info("終了 : SmartController ")

