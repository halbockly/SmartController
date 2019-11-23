# coding=utf-8
import json

# kaden.jsonを読みこんだり書き換えたりする役割。
# kaden.jsonは[ ((kadenId))1 : { name:"クーラー" , signal:"赤外線信号" status:0((0=off,1=on)) } ]の形での管理を想定。

class status():
    #index.py、switch.pyとのやり取り
# index.py(switch.py)から受け取ったidのステータスを取得して返すメソッド====================================================
    def checkStatus(self,id):
        loadRequestJson = getKadenStatus()              # kaden.JSONを取得
        resStatus = loadRequestJson[id]['status']       # リクエストのidの['status']を取得する
        return resStatus                                # レスポンス( 0 or 1 )を送る


    #switch.pyとのやり取り
# kaden.jsonを書き換えるメソッド=========================================================================================
    def changeStatusJson(self,id):
        result = true                                   # 書き換え完了フラグ
        loadRequestJson = getKadenStatus()              # kaden.JSONを取得
        status = loadRequestJson[id]['status']          # リクエストのkadenIdのステータスを取得

        try:
            if status == 0:
                loadRequestJson[id]['status'] = 1           # ステータスを書き換え
            elif status == 1:
                loadRequestJson[id]['status'] = 0           # ステータスを書き換え

            new_json_file = open('kaden.json', 'w')             # kaden.jsonを書き込みたいファイルとして開く
            jdon.dump(loadRequestJson,new_json_file,indent=2)   # kaden.jsonを上書き
            new_json_file.close()                               # 上書きしたファイルを閉じる

        except:
            result = False                               # 何故か書き換えに失敗したらFalseを返す

        return result                                    # 書き換え完了フラグを返す


    # class内の処理用メソッド
# kaden.jsonそのものを取得するメソッド====================================================================================
    def getKadenStatus(self):
        """Kaden.JSONを取得する"""
        openRequestJson = open('kaden.json', 'r')       # kaden.jsonを開く
        loadRequestJson = json.load(openRequestJson)    # kaden.jsonを読み込む
        return loadRequestJson                          # kaden.jsonを返り値として返す