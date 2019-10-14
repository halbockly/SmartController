import subprocess
import time
import configparser

cmd = './ngrok http 8080 --log=stdout'

from subprocess import Popen, PIPE

__ADDR__ = "addr="
__STARTED_TUNNEL__ = "started tunnel"

url = ""

p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
time.sleep(1)

for line in iter(p.stdout.readline, b''):

    decodeLine = line.rstrip().decode("utf8")

    msgIndex = decodeLine.find(__STARTED_TUNNEL__)
    print(decodeLine)

    if (msgIndex != -1):
        addrIndex = decodeLine.find(__ADDR__)
        url = decodeLine[addrIndex + len(__ADDR__):]

        print(url)

        inifile = configparser.ConfigParser()
        inifile.read("./settings/ngrokToHeroku.ini")

        inifile.set("ngrok", "url", url)

        print(inifile.get("ngrok", "url"))

        break

while (True):
    print("mawateru")
    time.sleep(1)