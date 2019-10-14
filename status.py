import index
import json

# kaden.jsonを読みこんだり書き換えたりする役割。

# kaden.jsonは[ ((kadenId))1 : { name:"クーラー" , signal:"赤外線信号" status:0((0=off,1=on)) } ]の形での管理を想定。

def getStatusJSOM():
    """kaden.jsonを取得する"""
    # 含まれるであろう要素：kadenId , name , signal , status
    openStatusJson = open('kaden.json', 'r')     # r:読み込み , w:書き込み , a:追記
    loadStatusJson = json.load(openStatusJson)    # load関数で読みこんだJSONは辞書型データとなる。
    return loadStatusJson

def getRequestStatus():
    """index.py もしくは switch.py からのリクエスト（JSON形式を想定）を取得する"""
    # 含まれるであろう要素：kadenId , manipulatedId (, from , to)
    openRequestJson = open('request.json', 'r')     # r:読み込み , w:書き込み , a:追記
    loadRequestJson = json.load(openRequestJson)    # load関数で読みこんだJSONは辞書型データとなる。

    nowStatusJson = getStatusJSOM()
    if loadRequestJson['manipulatedId'] != nowStatusJson['status'] and loadRequestJson['from'] == "" and loadRequestJson['to'] != "":
        # リクエストと状態が異なる且つタイマー無しの場合
        # switch.py に状態変更をさせる。成功したらchangeStatus()を行い、失敗したらその旨を伝える。

    elif loadRequestJson['manipulatedId'] != nowStatusJson['status'] and loadRequestJson['from'] != "" and loadRequestJson['to'] == "":
        # リクエストと状態が異なる且つ入タイマー付きの場合
    elif loadRequestJson['manipulatedId'] != nowStatusJson['status'] and loadRequestJson['from'] == "" and loadRequestJson['to'] != "":
        # リクエストと状態が異なる且つ切タイマー付きの場合
    elif loadRequestJson['manipulatedId'] == nowStatusJson['status']:   # else: でも良さそう？
        # リクエストと状態が合致している（状態変更の必要が無い場合）


def changeStatusJson():
    """kaden.jsonを書き換える"""
    # remoteController.py動かして家電を動かす　→　これはswitch.pyの役割なのでここではやらない。
    # kaden.jsonのフラグ書き換え　→　これが役割。
    # getStatusJson()の中で呼び出されて使われる。