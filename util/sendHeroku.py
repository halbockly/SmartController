import requests
import logging

##   kaden.json の設置パス（rootに置いてるのでそのまんま
__KADEN_JSON_PATH__ = "kaden.json"
##   取り出したURLの送信先
__REQUEST_URL__ = "https://smartcontrollerheroku.herokuapp.com/getNgrokuUrlToHeroku"

#
# Heroku連携用のクラス
#
class SendHeroku:

    def __init__(self):
        # メンバー変数
        ## kaden.jsonの中身
        self.kadenJsonFile = ""

    #
    # status.py
    #
    def sendHerokuStatusUpdate(self):
        self.sendHeroku("")
    #
    # Herokuに情報送信（NgrokURL有）
    #
    def sendHeroku(self,url):
        logging.info("開始: NgrokのURL＋kaden.jsonをHerokuに連携")
        # kaden.jsonを一緒にアップロード
        f = open(__KADEN_JSON_PATH__, "r", encoding="utf-8")  # {'upload_file': open(__KADEN_JSON_PATH__, "rb")}
        self.kadenJsonFile = f.read()
        f.close()
        print(self.kadenJsonFile)

        # URLを送信する。
        response = requests.post(__REQUEST_URL__, data={"url": url, 'file': self.kadenJsonFile})

        print(__REQUEST_URL__ + ' status_code:' + str(response.status_code))

        if response.status_code != 200:
            logging.error("エラー : status_code:" + response.status_code + " NgrokのURL＋kaden.jsonをHerokuに連携")

            return False
        else:
            logging.info("完了: NgrokのURL＋kaden.jsonをHerokuに連携")
            return True

