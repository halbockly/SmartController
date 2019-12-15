# coding=utf-8
from crontab import CronTab
import json
import switch
import logging


# Linuxのタスクマネージャー「cron」にタイマー予約をセットする
# cronがもし落ちてたらetcで再起動させて対応する必要がある
# やりとりするのは、input:index.py　、　output:cron　、　i/o:status.py

class CrontabControl():
    def __init__(self):
        self.cron = CronTab()
        self.job = None

    # crontabにジョブを書き込むメソッド
    """メソッド名：write_job()"""
    """引数　：command, schedule, file_name"""
    """戻り値：無し"""
    def write_job(self, command, schedule, file_name):
        self.job = self.cron.new(command=command)
        self.job.setall(schedule)
        self.cron.write(file_name)

    # crontab中のジョブを全て読み込むメソッド
    """メソッド名：read_jobs()"""
    """引数　：file_name"""
    """戻り値：無し"""
    def read_jobs(self, file_name):
        self.cron = CronTab(tabfile=file_name)

    # ジョブを監視するメソッド
    """メソッド名：monitor_jobs()"""
    """引数　：file"""
    """戻り値：無し"""
    def monitor_start(self, file):
        # スケジュールを読み込む
        self.read_jobs(file)
        for result in self.cron.run_scheduler():
            # スケジュールになるとこの中の処理が実行される

            # ログの出力名を設定（1）
            logger = logging.getLogger('LoggingTest')
            # ログレベルの設定（2）
            logger.setLevel(0)
            # ログのコンソール出力の設定（3）不要のためコメント化
            # sh = logging.StreamHandler()
            # logger.addHandler(sh)
            # ログのファイル出力先を設定（4）
            fh = logging.FileHandler('crontab_order.log')
            logger.addHandler(fh)


# ===================================
# 現在日時の取得
# dt_now = datetime.datetime.now()
# 30分後とか指定時刻を下記の dt にセットする。なお年月日は必須。
# input_gap = 30      # index.pyのリクエストから入力される「○分後」の○を右辺に。
# gap_minute = datetime.timedelta(minutes = input_gap)        # 「○分」のデータにする。
# dt_reserved = dt_now + gap_minute      現在日時(dt_now)と「○分」(gap_minute)を足して予定日時にする。
