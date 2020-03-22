# coding=utf-8
import json
import codecs
from util.sendHeroku import SendHeroku

# kaden.jsonを読みこんだり書き換えたりする役割。
# kaden.jsonは[ ((kadenId))1 : { name:"クーラー" , signal:"赤外線信号" status:0((0=off,1=on)) } ]の形での管理を想定。

class Status:
    def __init__(self):
        pass

    JSON_FILE = "kaden.json"

    # ▼index.pyとのやり取り▼
    # index.pyからの要求でkaden.jsonのデータを取得して返すメソッド================================================
    """引数　：無し"""
    """戻り値：loadRequestJson（kaden.jsonを開いて得たデータ）"""
    def checkStatus(self):
        loadRequestJson = self.getKadenStatus()              # kaden.JSONを取得
        return loadRequestJson                                # レスポンス( 0 or 1 )を送る

    # ▼switch.pyとのやり取り▼
    # switch.pyから受け取ったidのステータスを取得して返すメソッド================================================
    """引数　：id（kadenId）"""
    """戻り値：resStatus（0 or 1、kaden.jsonで確認した対象のステータス）"""
    def checkStatusForSwitch(self, kadenId):
        loadRequestJson = self.getKadenStatus()              # kaden.JSONを取得
        resStatus = loadRequestJson[kadenId]['status']       # リクエストのidの['status']を取得する
        return resStatus                                # レスポンス( 0 or 1 )を送る

    # kaden.jsonを書き換えるメソッド=====================================================================================
    """引数　：id（kadenId）"""
    """戻り値：result（true/false、kaden.jsonの対象のステータスの書き換え成否）"""
    def changeStatusJson(self, kadenId):
        result = True                                   # 書き換え完了フラグ
        loadRequestJson = self.getKadenStatus()              # kaden.JSONを取得
        status = loadRequestJson[kadenId]['status']          # リクエストのkadenIdのステータスを取得

        try:
            if status == "0":
                loadRequestJson[kadenId]['status'] = "1"           # ステータスを書き換え
            elif status == "1":
                loadRequestJson[kadenId]['status'] = "0"           # ステータスを書き換え

            data = self.get_kaden_json()
            data[self.kaden_id]['status'] = self.manipulate_id
            with open(self.JSON_FILE, 'w') as f:
                json.dump(data, f, indent='\t')

            new_json_file = open('kaden.json', 'w')             # kaden.jsonを書き込みたいファイルとして開く
            json.dump(loadRequestJson, new_json_file, indent='\t')   # kaden.jsonを上書き
            new_json_file.close()                               # 上書きしたファイルを閉じる

            # Status更新が掛かったタイミングでHerokuのkaden.jsonを更新して貰う。
            sh = SendHeroku()
            sh.sendHerokuStatusUpdate()

        except (FileExistsError, FileNotFoundError):
            result = False                               # 何故か書き換えに失敗したらFalseを返す

        return result                                    # 書き換え完了フラグを返す

    # ▼class内の処理用メソッド▼
    # kaden.jsonそのものを取得するメソッド================================================================================
    """引数　：なし"""
    """戻り値：loadRequestJson（読み込んだkaden.json）"""
    def getKadenStatus(self):
        openRequestJson = codecs.open(self.JSON_FILE, 'r', 'utf-8')       # kaden.jsonを開く
        loadRequestJson = json.load(openRequestJson)    # kaden.jsonを読み込む
        openRequestJson.close()
        return loadRequestJson                          # kaden.jsonを返り値として返す
