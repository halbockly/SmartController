from bottle import Bottle, run, route, abort, request
from crontab import CronTab
import json
import requests
from _switch import Switch
from _status import Status

app = Bottle()


@app.route('/index', method='POST')
def index():

    params = request.json

    try:
        manipulate_id = params["manipulateId"]

        # ステータス管理処理
        if manipulate_id == "0":
            st = Status(params)
            status = st.get_current_status()
            msg = {"kadenId": st.kaden_id, "status": status}

        # ONOFF処理
        elif manipulate_id in ["1", "2"]:
            sw = Switch(params)
            msg = sw.switching()

        # タイマー処理
        elif manipulate_id in ["3", "4"]:
            timer_class = Timer()
            msg = timer_class.timerSetting(params)
        else:
            msg = None

        result = {
            "status": 200,
            "message": msg
        }

    except Exception as e:
        result = {
            "status": 500,
            "message": e
        }

    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True, reloader=True)
