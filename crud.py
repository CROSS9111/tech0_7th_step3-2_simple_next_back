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
from mymodels import Image as ImageModel


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

def save_image_to_db(image_data):
    # セッション構築用のSessionクラスを作成
    Session = sessionmaker(bind=engine)
    # セッションのインスタンスを作成
    session = Session()

    # 画像データをImageモデルに保存
    new_image = ImageModel(image=image_data)
    try:
        session.add(new_image)
        session.commit()
        return new_image.id  # 画像のIDを返す
    except Exception as e:
        session.rollback()
        raise e  # エラーを再度投げて、呼び出し元でハンドリング
    finally:
        # セッションを閉じる
        session.close()