from bottle import Bottle, run, route, abort, request
import json

app = Bottle()


class remote_controller(interface_physical):

    def Execute(kaden_Id, operation_id):
        print(kaden_Id, operation_id)
