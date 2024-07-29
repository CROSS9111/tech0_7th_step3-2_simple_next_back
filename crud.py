# uname() error回避
import platform
print("platform", platform.uname())

from sqlalchemy import create_engine, insert, delete, update, select
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import json
import pandas as pd

from connect import engine
from mymodels import Location

def myinsert(mymodel, values):
    # セッション構築用のSessionクラスを作成
    Session = sessionmaker(bind=engine)
    # セッションのインスタンスを作成
    session = Session()
    
    query = insert(mymodel).values(values)
    try:
        # トランザクションを開始
        with session.begin():
            # データの挿入
            result = session.execute(query)
            print(f"Insert result: {result.rowcount} rows inserted")
    except sqlalchemy.exc.IntegrityError as e:
        print(f"一意制約違反により、挿入に失敗しました: {e}")
        session.rollback()  # ロールバック
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        session.rollback()  # ロールバック
    finally:
        # セッションを閉じる
        session.close()
    
    return "inserted"


def myload(mymodel):
    # セッション構築用のSessionクラスを作成
    Session = sessionmaker(bind=engine)
    # セッションのインスタンスを作成
    session = Session()
    
    try:
        # データの選択
        query = select(mymodel)
        result = session.execute(query)
        # 結果をリストに変換
        rows = result.scalars().all()
        return rows
    finally:
        # セッションを閉じる
        session.close()
