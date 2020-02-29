# coding=utf-8
import json
import requests
from physical.remoteController import remoteController
from _status import Status


class Switch:

    def __init__(self, param):
        self.st = Status(param)

    def switching(self):
        kaden_id = self.st.kaden_id
        manipulate_id = self.st.manipulate_id

        if manipulate_id == self.st.get_current_status():
            on_off = "ON" if manipulate_id == "1" else "OFF"
            msg = "kadenId: " + kaden_id \
                  + " already " + on_off
        else:
            if self.kaden_switching():
                msg = "Success" if self.st.update_status() else "Failed"
            else:
                msg = "Failed"

        return msg

    def kaden_switching(self):
        # rc = remoteController()
        # result = rc.execute(self.st.kaden_id)
        return True
