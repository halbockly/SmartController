# coding=utf-8
import json
import requests
import logging
#from physical.remoteController import remoteController
from _status import Status


class Switch:

    def __init__(self, param):
        logging.debug("スイッチ　パラメータ：" + json.dumps(param))
        self.st = Status(param)

    def switching(self):
        logging.debug("開始　スイッチ")
        kaden_id = self.st.kaden_id
        manipulate_id = self.st.manipulate_id

        if manipulate_id == self.st.get_current_status():
            on_off = "ON" if manipulate_id == "1" else "OFF"
            msg = "kadenId: " + kaden_id \
                  + " already " + on_off
            logging.info("完了　スイッチ：変更無し")
        else:
            if self.kaden_switching():
                msg = "Success" if self.st.update_status() else "Failed"
                logging.info("完了　スイッチ：赤外線送信成功")
            else:
                msg = "Failed"
                logging.info("エラー　スイッチ：赤外線送信失敗")

        return msg

    def kaden_switching(self):
        # rc = remoteController()
        # result = rc.execute(self.st.kaden_id)
        return True
