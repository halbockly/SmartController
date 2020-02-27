# coding=utf-8

import subprocess
import time
import configparser
import requests
from _timer import CrontabControl

# ----------------------------------------------------
# Herokuに対してngrokのURLを送る為の部品
# 再起動時デーモンから呼び出してもらう。
#

cmd = 'ngrok http 8080 --log=stdout'

from subprocess import Popen, PIPE

# ngrokのSTDOUTに下記が現れたらURLが出力される。
__STARTED_TUNNEL__ = "started tunnel"
# 下記の値がURL
__ADDR__ = "url="
# 取り出したURLの送信先
__REQUEST_URL__ = "https://smartcontrollerheroku.herokuapp.com/getNgrokuUrlToHeroku"
# __REQUEST_URL__ = "https://localhost:8081/getNgrokuUrlToHeroku"

# kaden.json PATH
__KADEN_JSON_PATH__ = "kaden.json"

# kaden.jsonを一緒にアップロード
f = open("kaden.json", "r", encoding="utf-8")  # {'upload_file': open(__KADEN_JSON_PATH__, "rb")}
kadenJsonFile = f.read()
f.close()
print(kadenJsonFile)

# ngrokのEXE?を起動する。起動待ちとして1秒待つ
p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
time.sleep(1)

# pの中にSTDOUTへのPIPEが渡されるので
# そこからリアルタイムで1行ずつ読み込み→解析する。
url = ""

for line in iter(p.stdout.readline, b''):
    decodeLine = line.rstrip().decode("utf-8")

    # STDOUT内にstarted tunnel　が現れたら
    msgIndex = decodeLine.find(__STARTED_TUNNEL__)
    print(decodeLine)

    # その行の url= 以降がURLになる
    if (msgIndex != -1):
        addrIndex = decodeLine.find(__ADDR__)
        url = decodeLine[addrIndex + len(__ADDR__):]

        break

# URLを送信する。
response = requests.post(__REQUEST_URL__, data={"url": url, 'file': kadenJsonFile})

print(__REQUEST_URL__ + ' status_code:' + str(response.status_code))

if response.status_code != 200:
    print("ERROR : STOP setNgrokUrlToHeroku")
    sys.exit(-1)
else:
    print("SUCCESS : URL Send setNgrokUrlToHeroku")

# このメソッドが終わるとngrokの起動状態も破棄されるのでとりあえず回しておく。
# 何かheartbeatとか終了SEQとかここに入れておくといいかも

tab_file = 'reserved.tab'  # 予定を書き込むファイル

try:
    while (True):
        time.sleep(1)

except Exception as e:
    # Ctrl + C 等で強制終了された場合はここへくる。
    print(e)

