# coding=utf-8
from switch import Switch
import json
import sys

###
#    cronから実行するswitch.pyの入り口
###

#コマンドライン引数の取り出し。
# args[1] kadenId
# args[2] manipulateId
args = sys.argv
kadenId = args[1]
manipulateId = args[2]

print("cronToSwitch.py Start kadenId:" + kadenId + " manipulateId:" + manipulateId)

# switch.pyの実行。
swc = Switch()
swc.Switching({"kadenId":kadenId,"manipulateId":manipulateId})

print("cronToSwitch.py end ")
