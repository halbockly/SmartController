import subprocess
import time
import configparser
import requests

# ----------------------------------------------------
# Herokuに対してngrokのURLを送る為の部品
# 再起動時デーモンから呼び出してもらう。
#

cmd = './ngrok http 8080 --log=stdout'

from subprocess import Popen, PIPE


# ngrokのSTDOUTに下記が現れたらURLが出力される。
__STARTED_TUNNEL__ = "started tunnel"
# 下記の値がURL
__ADDR__ = "addr="
# 取り出したURLの送信先
__REQUEST_URL__ = "http://localhost:8080/getNgrokuUrlToHeroku"

url = ""

# ngrokのEXE?を起動する。起動待ちとして1秒待つ
p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
time.sleep(1)

# pの中にSTDOUTへのPIPEが渡されるので
# そこからリアルタイムで1行ずつ読み込み→解析する。
for line in iter(p.stdout.readline, b''):

    decodeLine = line.rstrip().decode("utf8")

    # STDOUT内にstarted tunnel　が現れたら
    msgIndex = decodeLine.find(__STARTED_TUNNEL__)
    print(decodeLine)

    # その行の addr= 以降がURLになる
    if (msgIndex != -1):
        addrIndex = decodeLine.find(__ADDR__)
        url = decodeLine[addrIndex + len(__ADDR__):]

        print(url)

        #URLを送信する。※未検証　でもPOSTを送信するメソッドが.postなのはわかりやすくていいね。
        response = requests.post(__REQUEST_URL__,data=url)
        break

while (True):
    time.sleep(1)

