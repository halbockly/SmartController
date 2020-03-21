import logging

#
# ログの初期化
#   あんまりindex.pyに手を入れるのもあれなのでファイルを分けた。
#
def initLog():
    format = "%(asctime)s [%(levelname)s] %(message)s [%(filename)s.%(funcName)s(%(lineno)s)]"
    logging.basicConfig(filename='./log/SmartController.log', format=format, level=logging.INFO)

