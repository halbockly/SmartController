# coding=utf-8

from bottle import Bottle, abort
import adrsirlib as ir
from physical.remoteController import remoteController

import json

# とりあえずテスト用に家電JSONに赤外線を登録する

app = Bottle()

rc = remoteController()

# 1番ボタンの赤外線信号を取得する。
infraRedSign = rc.getInfraRed(1)

kaden = open('kaden.json', 'w')
# Jsonの取得
kadenJson = json.loads(kaden)

#家電IDは最新値＋１を振る
lastKey = ""
for key in kadenJson:
    lastKey = key
newKey = int(lastKey) + 1
newStringKey = string(newKey)

# 家電JSONに追加
kadenJson.update([(newStringKey
                     ,[("name","test")
                     ,("signal", infraRedSign)
                     ,("status", "0")])])

json.dump(kadenJson, kaden, indent='\t')  # kaden.jsonを上書き
kaden.close()  # 上書きしたファイルを閉じる
