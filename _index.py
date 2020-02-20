from bottle import Bottle, run, route, abort, request
from crontab import CronTab
import json
import requests
from _switch import Switch
from _status import Status

app = Bottle()

exec_settings = {
    "exec_status": ["0"],
    "exec_switch": ["1", "2"],
    "exec_timer": ["3", "4"]
}


@app.route('/index', method='POST')
def index():
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

    return json.dumps(result, ensure_ascii=False)


def exec_status(params):
    st = Status(params)
    status = st.get_current_status()
    return {"kadenId": st.kaden_id, "status": status}


def exec_switch(params):
    sw = Switch(params)
    return sw.switching()


def exec_timer(params):
    timer_class = Timer()
    return timer_class.timerSetting(params)


if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True, reloader=True)
