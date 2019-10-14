from bottle import Bottle, run, route, abort, request
import adrsirlib as ir

import json

app = Bottle()


# リモコン基盤操作クラス
class remoteController():

    # 操作メソッド
    def execute(self, kadenId):
        result = True

        try:
            # とりあえずこれが動けば成功
            print('家電ID:' + kadenId)

            # infraRedSign = getInfraRedSign(kaden_id,infraRedId)

            # 実機じゃないと動かないのでコメントアウト。そのうちブランチ切る
            # 赤外線.jsonの読み出し
            # ir.send(infraRedSign)

        except:
            result = False

        return result


    # 赤外線信号 の取得
    def getInfraRedSign(self, kadenId):

        # 読み取りモードで開く
        f = open("kaden.json", 'r')
        # Jsonの取得
        infraRedId = json.loads(f)
        # 家電情報の取得
        infraRedList = infraRedJson[kadenId]
        # 赤外線の取得
        infraRed = kaden[infraRedId]

        return infraRed

    # 赤外線信号の保存
    def saveInfraRed(self, port):
        result = ir.get(port)

    # OperationIdの新規採番
    def getNewAsignOperationId(self):

        # 一旦読み取りモードで開く
        f = open("infrarRed.json", 'r')

        infraRedJson = json.loads(f)

        maxId = max(infraRedJson)
        newAsignId = int(maxId) + 1

        return newAsignId

