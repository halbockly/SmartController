# coding=utf-8
import sys
import logging
import json
import threading
import time

from crontab import CronTab as Crontab

from datetime import datetime

__SWITCH_COMMAND__ = "python3 cronToSwitch.py"


# Linuxのタスクマネージャー「cron」にタイマー予約をセットする
# cronがもし落ちてたらetcで再起動させて対応する必要がある

class Timer:
    # ▼index.pyとのやり取り▼
    # index.pyから受け取った予約の命令をmakeorderに渡し、戻ってきた予約の成否をメッセージで返すメソッド=======================
    """引数　：param { kadenId:x, manipulateId:y }"""
    """戻り値：msg（文字列、処理結果を表す返答メッセージ）"""

    def timerSetting(self, param):  # このメソッドを読んでもらえればタイマー予約します！多分
        logging.debug("開始 タイマー　パラメータ：" + json.dumps(param))
        # sw = Switch()
        # orderJson = sw.getRequestStatus(param)
        result = self.makeOrder(param)
        msg = "予約しました" if result == True else "予約失敗"

        logging.info("完了 タイマー　" + msg)
        return msg

    # ▼cronとのやり取り▼
    # timerSettingから受け取った予約をcronに書き込み、その成否を返すメソッド================================================
    """引数　：orderJson { kadenId:x, manipulateId:y }"""
    """戻り値：result（true/false、cronへの予約書き込みの成否）"""

    def makeOrder(self, orderJson):  # switch.pyに飛ばすJSONを作り、勢いでcrontabも書いてしまうメソッド
        print("timer.py makeOrder START")
        kadenId = orderJson['kadenId']
        order = orderJson['manipulateId']  # 3:TimerON 4:TimerOFF

        order = "1" if order == "3" else "2"  # 1:ON 2:OFF    ※order=3なら1を、そうでないなら2をセットする

        strTime = orderJson['timer_datetime']  # cronで命令を飛ばす日時　例）'2019-09-08T11:00'
        setTime = datetime.strptime(strTime, '%Y-%m-%dT%H:%M')  # cronで命令を飛ばす日時　例）'2019-09-08T11:00'
        cronWriteResult = True
        try:

            json_str = {
                "kadenId": kadenId,
                "manipulateId": order,
            }
            # filename = kadenId + '_' + str(
            #    order) + '_' + strTime + '.json'  # 指定日時になったらcrontabでswitch.pyに飛ばす命令＝JSONファイル（のファイル名）
            # f = open(filename, 'w')  # 書き込みモードで上記ファイルを開く
            # json.dump(json_str, f, indent='\t')  # str を書き込む

            rsv_mnt = setTime.strftime('%M')  # 予定日時の分
            rsv_hou = setTime.strftime('%H')  # 予定日時の時
            rsv_day = setTime.strftime('%d')  # 予定日時の日
            rsv_mon = setTime.strftime('%m')  # 予定日時の月
            cron_string = '{} {} {} {} *'  # cronに設定する文字列のひな型
            rsv_datatime = cron_string.format(rsv_mnt, rsv_hou, rsv_day, rsv_mon)  # 予定日時と命令をセット、文字列完成
            rsv_command = __SWITCH_COMMAND__ + " '" + str(kadenId) + "' '" + str(order) + "'"
            tab_file = 'reserved.tab'  # 予定を書き込むファイル
            logging.info("タイマー　" + rsv_command + " " + rsv_datatime)
            cc = CrontabControl()
            #cc.read_jobs(tab_file)
            cc.write_job(rsv_command, rsv_datatime, tab_file)  # crontabにjobを書き込む

            print(str(setTime) + " timerStart")
            # ここで行うとTimerの実行で止まってしまうので他所で行う。crontabに記録されたjobを読み込む
            cc.monitor_start(tab_file)  # crontabを監視する
            logging.debug("タイマー : 監視開始")
        except Exception as e:
            cronWriteResult = False
            logging.info("エラー：タイマー " + e)
            print(e)

        print("timerStart")
        return cronWriteResult


# 楽しい楽しいcronゾーン=================================================================================================

# cronの設定の仕方：分 時 日 月 曜 command  ワイルドカードは「*」、andは「,」、○毎は「n/n」、範囲は「n-n」
# 例）10分毎＝（分のところに）*/10       例２）8時2分から20時2分まで3時間毎＝（分は）2 （時は）8-20/3
"""
cronSettingStart = "crontab -u root -e"     # -e cronを設定する, -l 設定されてるcronを表示する, -r cron削除, -u ユーザを指定する
cronActionSet = "* * * * * python /home/switch.py"  # *ばかりだと毎分実行。分時日月曜。index.pyから指定されたタイミングを入れる。

dt_reserved = 'index.pyから飛んでくる予約日時'
min = dt_reserved.strftime('%M')        # 予定日時の分
hou = dt_reserved.strftime('%H')        # 予定日時の時
day = dt_reserved.strftime('%d')        # 予定日時の日
mon = dt_reserved.strftime('%m')        # 予定日時の月
cron_str = '{} {} {} {} *'              # cronに設定する文字列のひな型。
cron_cmd = cron_str.format(min,hou,day,mon)        # 予定日時と命令をセット。文字列完成。

req = 'index.pyから飛んでくる命令の詳細'  # JSONを想定
command = 'python /home/switch.py'      # 'python3 ./helloworld.py > ./test.txt'みたいに。　実行ファイル>出力先
schedule = cron_cmd
file = 'reserved.tab'                   # 予定を書き込むファイル

c = CrontabControl()                    # インスタンス作成
c.write_job(command, schedule, file)    # ファイルに書き込む
c.read_jobs(file)                       # ファイルを読み込む（タスクスケジュールを読み込む）
c.monitor_start(file)                   # タスクスケジュールの監視を開始
"""


# ===================================
class CrontabControl:
    def __init__(self):
        self.cron = Crontab()
        self.job = None

    # ファイルにジョブを書き込むメソッド
    def write_job(self, command, schedule, file_name):
        self.job = self.cron.new(command=command)
        self.job.setall(schedule)
        # self.cron.write(file_name)

    # ファイル中のジョブを全て読み込むメソッド
    def read_jobs(self, file_name):
        self.cron.read(file_name)

    # ジョブを監視を開始するメソッド
    def monitor_start(self, file):
        self.jobFile = file
        # self.cron = Crontab(tabfile=self.jobFile)
        self.monitoringThread = threading.Thread(target=self.monitoring_jobs)
        self.monitoringThread.start()

    # ジョブ監視を行うスレッド
    def monitoring_jobs(self):
        # スケジュールを読み込
        print("scheduling start")

        for result in self.cron.run_scheduler():
            # ログ出力
            logging.info(result + "タイマーが実行されました。")
            print(result + "タイマーが実行されました。")
            break

    # スレッド停止
    def monitoring_stop(self):
        self.monitoringThread.join()

# ===================================
# 現在日時の取得
# dt_now = datetime.datetime.now()
# 30分後とか指定時刻を下記の dt にセットする。なお年月日は必須。
# input_gap = 30      # index.pyのリクエストから入力される「○分後」の○を右辺に。
# gap_minute = datetime.timedelta(minutes = input_gap)        # 「○分」のデータにする。
# dt_reserved = dt_now + gap_minute        # 現在日時(dt_now)と「○分」(gap_minute)を足して予定日時にする。


