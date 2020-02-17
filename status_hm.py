# coding=utf-8
import json

# kaden.jsonを読みこんだり書き換えたりする役割。
# kaden.jsonは[ ((kadenId))1 : { name:"クーラー" , signal:"赤外線信号" status:0((0=off,1=on)) } ]の形での管理を想定。

class Status:
    JSON_FILE = "kaden.json"

    # ▼index.py、switch.pyとのやり取り▼
    # index.py(switch.py)から受け取ったidのステータスを取得して返すメソッド================================================
    """引数　：id（kadenId）"""
    """戻り値：resStatus（0 or 1、kaden.jsonで確認した対象のステータス）"""
    def checkStatus(self, kadenId):
        loadRequestJson = self.getKadenStatus()              # kaden.JSONを取得
        resStatus = loadRequestJson[kadenId]['status']       # リクエストのidの['status']を取得する
        return resStatus                                # レスポンス( 0 or 1 )を送る

    # ▼switch.pyとのやり取り▼
    # kaden.jsonを書き換えるメソッド=====================================================================================
    """引数　：id（kadenId）"""
    """戻り値：result（true/false、kaden.jsonの対象のステータスの書き換え成否）"""
    def changeStatusJson(self, kadenId, manipulateId):
        result = True                                   # 書き換え完了フラグ
        kadenJson = self.getKadenStatus()              # kaden.JSONを取得
        # status = kadenJson[kadenId]['status']          # リクエストのkadenIdのステータスを取得

        try:
            kadenJson[kadenId]['status'] = manipulateId           # ステータスを書き換え

            f = open(self.JSON_FILE, 'w')             # kaden.jsonを書き込みたいファイルとして開く
            json.dump(kadenJson, f, indent='\t')   # kaden.jsonを上書き
            f.close()                               # 上書きしたファイルを閉じる

        except (FileExistsError, FileNotFoundError):
            result = False                               # 何故か書き換えに失敗したらFalseを返す

        return result                                    # 書き換え完了フラグを返す

    # ▼class内の処理用メソッド▼
    # kaden.jsonそのものを取得するメソッド================================================================================
    """引数　：なし"""
    """戻り値：loadRequestJson（読み込んだkaden.json）"""
    def getKadenStatus(self):
        f = open(self.JSON_FILE, 'r')       # kaden.jsonを開く
        kadenJson = json.load(f)    # kaden.jsonを読み込む
        f.close()
        return kadenJson                          # kaden.jsonを返り値として返す
