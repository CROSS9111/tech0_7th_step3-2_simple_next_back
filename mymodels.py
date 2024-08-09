from sqlalchemy import Column, String, Float,Integer
from sqlalchemy.orm import declarative_base
import uuid

# データベースのベースクラスを定義
Base = declarative_base()

# Locationモデルを定義
class Location(Base):
    __tablename__ = 'locations' 
    # 主キーとしてUUIDを文字列として使用し、デフォルト値をuuid.uuid4に設定
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # 緯度を格納するカラム。制約を追加する場合はnullable=Falseなどを使用
    latitude = Column(Float, nullable=False)
    # 経度を格納するカラム。制約を追加する場合はnullable=Falseなどを使用
    longitude = Column(Float, nullable=False)


class Product_master(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)