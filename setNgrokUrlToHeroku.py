# coding=utf-8

import subprocess
import time
import configparser
import requests
import logging

from subprocess import Popen, PIPE
from util.sendHeroku import SendHeroku


def execNgrok():
    result = True

    logging.debug("開始: Ngrok")
    # 定数部
    ##   ngrokのSTDOUTに下記が現れたらURLが出力される。
    __STARTED_TUNNEL__ = "started tunnel"
    ##   下記の値がURL
    __ADDR__ = "url="
    ##   ngrok起動コマンド
    __CMD__ = 'ngrok http 8080 --log=stdout'

    __ERR__ = 'ERR_NGROK_108'

    # ----------------------------------------------------
    # Herokuに対してngrokのURLを送る為の部品
    # 再起動時デーモンから呼び出してもらう。
    #

    # ngrokのEXE?を起動する。起動待ちとして1秒待つ
    p = Popen(__CMD__.split(' '), stdout=PIPE, stderr=PIPE)
    time.sleep(1)

    url = ""
    # pの中にSTDOUTへのPIPEが渡されるので
    # そこからリアルタイムで1行ずつ読み込み→解析する。
    for line in iter(p.stdout.readline, b''):
        decodeLine = line.rstrip().decode("utf-8")
        print(decodeLine)
        # STDOUT内にstarted tunnel　が現れたら
        msgIndex = decodeLine.find(__STARTED_TUNNEL__)
        errIndex = decodeLine.find(__ERR__)
        # その行の url= 以降がURLになる
        if (msgIndex != -1):
            addrIndex = decodeLine.find(__ADDR__)
            url = decodeLine[addrIndex + len(__ADDR__):]
            break
        elif (errIndex != -1):
            result = False
            logging.error(decodeLine)
            break

    if result == False:
        return result

    # Herokuへの送信
    sH = SendHeroku()
    print("url:" + url)
    result = sH.sendHeroku(url)

    logging.info("完了: Ngrok初期化")
