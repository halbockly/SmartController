# coding=utf-8
import bottle
import index
import json
import requests

# 電源の入り切りをする子
# と言っても、受け取ったリクエストをremoteController.pyに横流しするだけ
# 電源のON/OFFの成否を受け、statusを変更したりしなかったり。
# つまり、「電源の状態を切り替えて」という命令しか送らない。

# 引数をどう設定するかは、前田くんが作る予定のindex.pyから見て使いやすいようにすること。

# index.py →　switch.py　の流れと
# index.py →　timer.py →　cron →　switch.py　の流れと
# timer.py ←→　status.py ←→　switch.py　の流れがあって、最後にswitch.py　→　remoteController.pyに流れる

# やりとりするのは、input:index.py , cron　、　output:remoteController.py　、　i/o:status.py
# 「既にON/OFFになっている」可能性も考慮すること。
# なので、「状態確認　→　状態変更/状態維持　（→　status書き換え）」がこのファイルのすべきこと。

def getRequestStatus():
    """index.py もしくは cron からのリクエスト（JSON形式を想定）を取得"""
    param = json.load(request.json)
    openjson = open('request.json', 'r')
    loadJson = json.load(openjson)
    return loadJson

def orderChangingStatus():
    """remoteController.py に状態変更の命令を送る"""
    loadJson = getRequestStatus()                    # JSON取得
    url = 'remoteController.py'
    params = json.dumps(loadJson)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, params, headers)   # remoteController.pyにJSONを送る
