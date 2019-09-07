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

            infraRedSign = getInfraRedSign(kaden_id,operationId)

            # 実機じゃないと動かないのでコメントアウト。そのうちブランチ切る
            # 赤外線.jsonの読み出し
            ir.send(infraRedSign)

        except:
            result = False

        return result


    # 赤外線信号の読み出しメソッド（Privateにしたい。
    def getInfraRedSign(self, kadenId, operationId):

        f = open("infraRed.json", 'r')

        infraRedJson = json.loads(f)

        kaden = infraRedJson['1']

        operation = kaden[operation_id]

        return operation
