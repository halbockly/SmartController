# coding=utf-8

import subprocess
import time
import configparser
import requests

from subprocess import Popen, PIPE
from util.sendHeroku import SendHeroku

# 定数部
##   ngrokのSTDOUTに下記が現れたらURLが出力される。
__STARTED_TUNNEL__ = "started tunnel"
##   下記の値がURL
__ADDR__ = "url="

##   ngrok起動コマンド
__CMD__ = 'ngrok http 8080 --log=stdout'

# ----------------------------------------------------
# Herokuに対してngrokのURLを送る為の部品
# 再起動時デーモンから呼び出してもらう。
#

# ngrokのEXE?を起動する。起動待ちとして1秒待つ
p = Popen(__CMD__.split(' '), stdout=PIPE, stderr=PIPE)
time.sleep(1)

url=""
# pの中にSTDOUTへのPIPEが渡されるので
# そこからリアルタイムで1行ずつ読み込み→解析する。
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


# Herokuへの送信
sH = SendHeroku()
result = sH.sendHeroku(url)

# このメソッドが終わるとngrokの起動状態も破棄されるのでとりあえず回しておく。
# 何かheartbeatとか終了SEQとかここに入れておくといいかも
try:
    while (True):
        time.sleep(1)

except Exception as e:
    # Ctrl + C 等で強制終了された場合はここへくる。
    print(e)
