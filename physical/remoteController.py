from bottle import Bottle, run, route, abort, request
import physical.adrsirlibmaster.adrsirlib as ir

import json

app = Bottle()


# リモートコントローラークラス
class remoteController():

    # リモコン家電操作メソッド
    def execute(self, kaden_id, operation_id):
        # 赤外線.jsonの読み出し
        infraRed = ir.send("")

    # 赤外線信号の読み出しメソッド（Privateにしたい。
    def getInfraRedSign(self, kaden_id, operation_id):
        return "せきがいせんしんごうだよ"
