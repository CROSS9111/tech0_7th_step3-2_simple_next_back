# uname() error回避
import platform
print(platform.uname())

from sqlalchemy import create_engine
import os

main_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_path)
print(f"Current directory: {main_path}")

engine = create_engine("sqlite:///geo.db", echo=True)

