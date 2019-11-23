# coding=utf-8
import bottle
import index
import json
import requests
from physical.remoteController import remoteController
import status

# 電源の入り切りをする子
# と言っても、受け取ったリクエストをremoteController.pyに横流しするだけ
# つまり、「電源の状態を切り替えて」という命令しか送らない。
# そのあと電源のON/OFFの成否を受け、statusを変更したりしなかったり。

# 「既にON/OFFになっている」可能性も考慮すること。

class switch():
    def Switching(self,param):              # リクエストのJSON（{ kadenId:x, status:y }）を引数とする
        orderJson = getRequestStatus(param) # リクエストのJSONをorderJsonに保持
        kadenId = orderJson["kadenId"]      # 操作したい家電のID
        orderStatus = orderJson["manipulateId"]   # どう操作したいか（1:ONにしたい、2:OFFにしたい）

        bool = priorConfirmation(kadenId,orderStatus)         # status.pyへ現在の家電のステータス確認
        if bool:                                                # 既に求める状態になっている場合
            str = "ON" if orderStatus == 1 else "OFF"           # status=1なら「ON」、=2なら「OFF」の文字列をセット
            msg = "既に" + str + "になっています"                 # 返答メッセージ
            return msg
        else:
            result = kadenSwitching(kadenId)                  # remoteController.pyへ赤外線送信依頼
            if result:                                          # 赤外線送信の成否
                st = status()
                rewrite = st.changeStatusJson(kadenId)          # 成功：status.pyへのステータス書き換え依頼
                msg = "操作完了" if rewrite else "書換失敗"      # 書き換えの成否に応じてmsgをセット
                return msg
            else:
                msg = "操作失敗"                                 # 失敗：赤外線送信失敗メッセージをセット
                return msg

    # class内の処理用メソッド
    def priorConfirmation(self,kadenId,orderStatus):
        """事前確認。現在の家電の状態を見てremoteContrpller.pyに命令を送るか決める"""
        st = status()
        nowStatus = st.checkStatus(kadenId) # ステータス確認依頼
        if orderStatus == 1 and nowStatus == 1:        # 求める状態と現在の状態を比較
            return false                    # 既に求める状態になっている⇒戻り値false
        elif orderStatus == 2 and nowStatus == 0:
            return false                    # 既に求める状態になっている⇒戻り値false
        else:
            return true                     # 求める状態と現在の状態が異なる⇒戻り値true


    def kadenSwitching(self,kadenId):
        """kadenIを引数にしてremoteController.pyに電源操作の命令を送る"""
        rc = remoteController()
        result = rc.execute(kadenId)
        return result


    def getRequestStatus(self,param):
        """index.py もしくは cron からのリクエスト（JSON形式を想定）を取得"""
        openjson = open(param, 'r')
        loadJson = json.load(openjson)
        return loadJson
