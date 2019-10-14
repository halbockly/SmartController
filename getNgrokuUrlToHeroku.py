
# とりあえずのサンプルソース（動作確認済み
import configparser

inifile = configparser.ConfigParser()
inifile.read("./settings/ngrokToHeroku.ini")
print(inifile.get("ngrok", "url"))