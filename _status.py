# coding=utf-8
import json
from util.sendHeroku import SendHeroku

class Status:

    JSON_FILE = "kaden.json"

    def __init__(self, param):
        self.kaden_id = param["kadenId"]
        self.manipulate_id = param["manipulateId"]

    def get_current_status(self):
        data = self.get_kaden_json()
        status = data[self.kaden_id]['status']
        return status

    def update_status(self):
        try:
            data = self.get_kaden_json()
            data[self.kaden_id]['status'] = self.manipulate_id
            with open(self.JSON_FILE, 'w') as f:
                json.dump(data, f, indent='\t')

            # Status更新が掛かったタイミングでHerokuのkaden.jsonを更新して貰う。
            sh = SendHeroku()
            sh.sendHerokuStatusUpdate()

            result = True
        except Exception as e:
            raise e

        return result

    @staticmethod
    def get_kaden_json():
        with open(Status.JSON_FILE, 'r') as f:
            data = json.load(f)

        return data
