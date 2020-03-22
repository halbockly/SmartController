# coding=utf-8
import json
import requests
from physical.remoteController import remoteController
from status import Status

# 電源の入り切りをする子
# と言っても、受け取ったリクエストをremoteController.pyに横流しするだけ
# つまり、「電源の状態を切り替えて」という命令しか送らない。
# そのあと電源のON/OFFの成否を受け、statusを変更したりしなかったり。

# 「既にON/OFFになっている」可能性も考慮すること。


class Switch:
    def __init__(self,):
        self.st = Status()

    # kadenIdとmanipulateIdで家電を操作するメソッド。戻り値としてお言葉がもらえる。=========================================
    """引数　：param { kadenId:x, manipulateId:y }"""
    """戻り値：msg（文字列、処理結果を表す返答メッセージ）"""
    def switching(self, param):                     # リクエストのJSON（{ kadenId:x, manipulateId:y }）を引数とする
        # orderJson = self.getRequestStatus(param)         # リクエストのJSONをorderJsonに保持
        print(param)
        kadenId = param["kadenId"]              # 操作したい家電のID
        orderStatus = param["manipulateId"]     # どう操作したいか（1:ONにしたい、2:OFFにしたい）
                                                # ※（3:ON予約、4:OFF予約）はindex.py⇒timer.pyの直通で処理

        bool_status = self.priorConfirmation(kadenId, orderStatus)   # status.pyへ現在の家電のステータス確認
        if bool_status:                                         # 既に求める状態になっている場合
            on_off = "ON" if orderStatus == "1" else "OFF"        # status=1なら「ON」、=2なら「OFF」の文字列をセット
            msg = "既に" + on_off + "になっています"             # 返答メッセージ
            return msg
        else:
            result = self.kadenSwitching(kadenId)                    # remoteController.pyへ赤外線送信依頼
            if result:                                          # 赤外線送信の成否

                rewrite = st.changeStatusJson(kadenId)   # 成功：status.pyへのステータス書き換え依頼
                msg = "操作完了" if rewrite else "書換失敗"      # 書き換えの成否に応じてmsgをセット
                return msg
            else:
                msg = "操作失敗"                                # 失敗：赤外線送信失敗メッセージをセット
                return msg

    # ▼class内の処理用メソッド▼
    def priorConfirmation(self, kadenId, orderStatus):
        """事前確認。現在の家電の状態を見てremoteController.pyに命令を送るか決める"""

        nowStatus = st.checkStatusForSwitch(kadenId)         # ステータス確認依頼
        if orderStatus == 1 and nowStatus == 1:     # 求める状態と現在の状態を比較
            return False                            # 既に求める状態になっている⇒戻り値false
        elif orderStatus == 2 and nowStatus == 0:
            return False                            # 既に求める状態になっている⇒戻り値false
        else:
            return True                             # 求める状態と現在の状態が異なる⇒戻り値true

    # kadenIdを引数にしてremoteController.pyに電源操作の命令を送るメソッド=================================================
    """引数　：kadenId"""
    """戻り値：result（true/false、赤外線送信の成否）"""
    def kadenSwitching(self, kadenId):
        rc = remoteController()
        result = rc.execute(kadenId)
        return result

    # # index.py もしくは cron からのリクエスト（JSON形式を想定）を取得するメソッド===========================================
    # """引数　：jsonfile （JSON形式のファイルのファイル名を指定する）"""
    # """戻り値：loadjson（辞書型、引数のJSONデータをpythonで扱いやすいようにした状態）"""
    # def getRequestStatus(self, jsondata):
    #
    #     openjson = open(jsondata, 'r')
    #     loadJson = json.load(openjson)
    #     return loadJson
