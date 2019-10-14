# coding=utf-8
import index

# Linuxのタスクマネージャー「cron」にタイマー予約をセットする

# cronがもし落ちてたらetcで再起動させて対応する必要がある

# やりとりするのは、input:index.py　、　output:cron　、　i/o:status.py

# cronの設定の仕方：分 時 日 月 曜 command  ワイルドカードは「*」、andは「,」、○毎は「n/n」、範囲は「n-n」
# 例）10分毎＝（分のところに）*/10       例２）8時2分から20時2分まで3時間毎＝（分は）2 （時は）8-20/3

cronSettingStart = "crontab -e"     # -e conを設定する, -l 設定されてるcronを表示する, -r cron削除, -u ユーザを指定する
cronActionSet = "* * * * * python /home/switch.py"  # *ばかりだと毎分実行。index.pyから指定されたタイミングを入れる。

