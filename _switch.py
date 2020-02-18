# coding=utf-8
import json
import requests
# from physical.remoteController import remoteController
from _status import Status


class Switch:

    def __init__(self, param):
        self.st = Status(param)

    def switching(self):
        if not self.check():
            on_off = "ON" if self.st.manipulate_id == "1" else "OFF"
            msg = "kadenId: " + self.st.kaden_id \
                  + " already " + on_off
        else:
            if self.kaden_switching(self.st.kaden_id):
                msg = "Success" if self.st.update_status() else "Failed"
            else:
                msg = "Failed"

        return msg

    def check(self):
        current_status = self.st.get_current_status()

        if self.st.manipulate_id == "1" and current_status == "1":
            return False
        elif self.st.manipulate_id == "2" and current_status == "2":
            return False
        else:
            return True

    def kaden_switching(self, kaden_id):
        # rc = remoteController()
        # result = rc.execute(kaden_id)
        return result
