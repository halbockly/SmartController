from physical.remoteController import remoteController

kadenId = '1'

# リモコン基盤操作クラスをインスタンス化する。
#     コンストラクタの引数は無し(今のところ)
rc = remoteController()

# 操作メソッドを呼び出す。
#     引数：  kadenId      : string index.pyからもらった物
#             operationId : string 電源切り替えだけなら"1"固定で大丈夫。
#     戻り値：             : bool   実行結果 true:成功、false:失敗
result = rc.execute(kadenId, '1')
