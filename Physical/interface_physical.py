from bottle import Bottle, run, route, abort, request

app = Bottle()


# でもこの作りだと家電の種別ごとに呼び出すクラス変えてもらわないといけないのでたぶんやめる。

# 家電操作のインターフェース的な物。
# 各家電クラスはこのインターフェース的な物を継承し、その中のメソッドはこの中のメソッドをオーバーライドしないとエラーになるので
# 家電が違ってもメソッドと引数は同じであることがある程は度保障される。（でも現時点では足りなかったら足す。
class interface_physical(meta_class=meta):

    @absractmethod
    # 家電の操作メソッド。
    # リモコン操作の場合はこの抽象メソッドを呼び出すことで、赤外線が発信される。（という処理をリモコンクラスに書く
    # 引数： kaden_id 家電ID
    #       operation_id 操作ID
    def execute(kaden_id, operation_id):
        pass
