from bottle import Bottle, run, route, abort, request
# import adrsirlib as ir

import json

app = Bottle()


# リモコン基盤操作クラス
class remoteController():

    # 操作メソッド
    def execute(self, kadenId, operationId):
        result = True

        try:
            # とりあえずこれが動けば成功
            print('家電ID:' + kadenId + ' 操作ID：' + operationId)

            # infraRedSign = getInfraRedSign(kaden_id,operationId)

            # 実機じゃないと動かないのでコメントアウト。そのうちブランチ切る
            # 赤外線.jsonの読み出し
            ir.send(infraRedSign)

        except:
            result = False

        return result


    # 赤外線信号 の取得
    def getInfraRedSign(self, kadenId, operationId):

        # 読み取りモードで開く
        f = open("infraRed.json", 'r')
        # Jsonの取得
        infraRedJson = json.loads(f)
        # 家電情報の取得
        operationList = infraRedJson[kadenId]
        # 赤外線の取得
        infraRed = kaden[operationId]

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

