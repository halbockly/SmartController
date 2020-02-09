# coding=utf-8

from bottle import Bottle, abort
from physical.remoteController import remoteController

import json

# とりあえずテスト用に家電JSONに赤外線を登録する

app = Bottle()

rc = remoteController()

# 1番ボタンの赤外線信号を取得する。
infraRedSign = rc.getInfraRed(0)
print(infraRedSign)

try:
    # Jsonの取得
    kaden = open('kaden.json', 'r')
    kadenJson = json.load(kaden)

    # 家電IDは最新値＋１を振る
    lastKey = ""
    for key in kadenJson:
        lastKey = key
    newKey = int(lastKey) + 1

    print("newKey:" + str(newKey))
    newStringKey = str(newKey)
except:
    newStringKey = "1"
    kadenJson = {}

kadenJson[newStringKey] = {"name": "test", "signal": infraRedSign, "status": "0"}

# 家電JSONに追加
kadenJson.update(kadenJson)
kaden.close()

kadenW = open('kaden.json', 'w')

json.dump(kadenJson, kadenW, indent='\t')  # kaden.jsonを上書き
kadenW.close()  # 上書きしたファイルを閉じる

