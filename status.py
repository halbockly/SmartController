# coding=utf-8
import json

# kaden.jsonを読みこんだり書き換えたりする役割。

# kaden.jsonは[ ((kadenId))1 : { name:"クーラー" , signal:"赤外線信号" status:0((0=off,1=on)) } ]の形での管理を想定。

class status():
    #index.py、switch.pyとのやり取り
    def checkStatus(self,id):
        """index.pyから受け取ったidのステータスを取得して返す"""
        loadRequestJson = getKadenStatus()              # kaden.JSONを取得
        resStatus = loadRequestJson[id]['status']       # リクエストのidの['status']を取得する
        return resStatus                                # レスポンス( 0 or 1 )を送る


    #switch.pyとのやり取り
    def changeStatusJson(self,id):
        """kaden.jsonを書き換える"""
        loadRequestJson = getKadenStatus()              # kaden.JSONを取得
        status = loadRequestJson[id]['status']          # リクエストのkadenIdのステータスを取得
        if status == 0:
            loadRequestJson[id]['status'] = 1
        elif status == 1:
            loadRequestJson[id]['status'] = 0


    # class内の処理用メソッド
    def getKadenStatus(self):
        """Kaden.JSONを取得する"""
        openRequestJson = open('kaden.json', 'r')  # kaden.jsonを開く
        loadRequestJson = json.load(openRequestJson)  # kaden.jsonを読み込む
        return loadRequestJson