# platformモジュールを使用してシステム情報を表示
import platform
print(platform.uname())

# mymodelsからBaseとLocationをインポート
from mymodels import Base, Location, Product_master
# connectモジュールからengineをインポート
from connect import engine

# テーブルを作成するメッセージを表示
print("Creating tables >>> ")

# テーブルを作成
Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
