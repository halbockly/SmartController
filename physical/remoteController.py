from bottle import Bottle, run, route, abort, request
import physical.adrsirlib.adrsirlib as ir

import json

app = Bottle()


# リモコン基盤操作クラス
class remoteController():

    # 操作メソッド
    def execute(self, kadenId):
        result = True

        try:
            # とりあえずこれが動けば成功
            # print('家電ID:' + kadenId)

            infraRedSign = self.getInfraRedSign(kadenId)
            print(infraRedSign)
            # 実機じゃないと動かないのでコメントアウト。そのうちブランチ切る
            # 赤外線.jsonの読み出し
            ir.send(infraRedSign)

        except:
            result = False
            print("おちたよ")

        return result

    # 赤外線信号 の取得
    def getInfraRedSign(self, kadenId):

        # 読み取りモードで開く
        f = open("kaden.json", 'r')

        # Jsonの取得
        kadenJson = json.load(f)

        # 家電情報の取得
        kaden = kadenJson[kadenId]

        # 赤外線の取得
        signal = kaden["signal"]

        return signal

    # 赤外線信号の保存
    def getInfraRed(self, port):
        result = ir.get(port)

        return result

    # OperationIdの新規採番
    def getNewAsignOperationId(self):

        # 一旦読み取りモードで開く
        f = open("infrarRed.json", 'r')

        infraRedJson = json.loads(f)

        maxId = max(infraRedJson)
        newAsignId = int(maxId) + 1

        return newAsignId


