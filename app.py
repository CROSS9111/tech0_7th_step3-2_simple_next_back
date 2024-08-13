# 起動コマンド
# flask run --debugger --reload
from flask import Flask, request, jsonify, send_file, Response
import crud, mymodels
import os
from flask_cors import CORS
from PIL import Image as PILImage
from io import BytesIO
from sqlalchemy.orm import sessionmaker
from mymodels import Image
from connect import engine
from crud import save_image_to_db

app = Flask(__name__)
CORS(app)

# upload用のフォルダを作成する
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

############### ダミーデータ ###############
test_location = [
    {"id": "test_user1", "latitude": 35.6895, "longitude": 139.6917},
    {"id": "test_user2", "latitude": 34.0522, "longitude": -118.2437}
]

test_product_code = [
    {"id": "0001", "product_code": 12345, "product_name": "tech0"},
    {"id": "0002", "product_code": 23456, "product_name": "tech1"},
    {"id": "0003", "product_code": 34567, "product_name": "tech2"},
    {"id": "0004", "product_code": 45678, "product_name": "tech3"},
]
##########################################

# flask起動時にアクセスすると表示される
@app.route("/")
def index():
    return "<p>Flask top page!</p>"

# ルートにアクセスするとdbやテーブルがmymodelsに合わせて作成される
@app.route("/create", methods=["GET"])
def create():
    try:
        # ディレクトリが存在しない場合は作成
        if not os.path.exists('geo.db'):
            open('geo.db', 'w').close()
            db_message = "Database file created and tables created successfully"
        else:
            db_message = "Database file already exists, tables created successfully"
        
        # テーブルを作成
        from create_table import Base, engine
        Base.metadata.create_all(bind=engine)
        return jsonify({"message": db_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ダミーデータをdbに追加する
@app.route("/add", methods=["GET"])
def add():
    try:
        for loc in test_location:
            crud.myinsert(mymodels.Location, loc)
        for code in test_product_code:
            crud.myinsert(mymodels.Product_master, code)
        return jsonify({"message": "Test locations & code added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# dbのLocationを読み、そのデータをレスポンスする
@app.route("/read", methods=["GET"])
def read():
    try:
        locations = crud.myload(mymodels.Location)
        locations_list = [{"id": loc.id, "latitude": loc.latitude, "longitude": loc.longitude} for loc in locations]
        return jsonify(locations_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# dbを削除する
@app.route("/delete_db", methods=["GET"])
def delete_db():
    try:
        if os.path.exists('geo.db'):
            os.remove('geo.db')
            return jsonify({"message": "Database file deleted successfully"}), 200
        else:
            return jsonify({"message": "Database file does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#####################################################
##########     商品コードから商品名     ################
#####################################################
# Product_masterのデータを読み、フロントから送られてきた商品コードとあっている商品名をレスポンスする
@app.route("/store", methods=["POST"])
def store():
    data = request.get_json()
    product_code = data 
    # product_masterテーブルからデータをロード
    products = crud.myload(mymodels.Product_master)  # ProductMasterモデルを使用

    # 指定された商品コードに一致する商品を検索
    product_name = None
    for product in products:
        if product.product_code == product_code:
            product_name = product.product_name
            break
    return jsonify({"name": product_name})



#####################################################
##########       画像のやり取り        ################
#####################################################
# バックエンドの画像をフロントに送信する
@app.route('/getimage', methods=['GET'])
def getimage():
    img = PILImage.open("sendingimage/CEO.jpeg")
    
    # RGBA の場合、RGB に変換
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    img_io = BytesIO()
    img.save(img_io, "JPEG", quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype="image/jpeg")

# 画像をフロントから受け取る
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # 画像を読み込み
        img = PILImage.open(file.stream)

        # 画像がRGBAモードの場合はRGBに変換
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        try:
            # 画像データをDBに保存
            image_id = save_image_to_db(img_byte_arr)
            return jsonify({'message': 'Image uploaded and saved successfully', 'image_id': image_id}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

#####################################################
##########         Basic認証          ################
#####################################################
# 認証ロジック　範囲ごとに分けている
def check_auth(username, password):
    # シンプルな認証ロジック
    if username == 'admin' and password == 'adminpass':
        return 'admin'
    elif username == 'user' and password == 'userpass':
        return 'user'
    return None

# 認証が不適合だった場合、HTTP認証のヘッダー(WWW-Authenticate)を含めて、認証が必要なことをクライアント側に通知する(401 unauthorized)
# WWW-Authenticate:アクセスに必要な認証の種類などを知らせる機能を持つ
def authenticate(realm):
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': f'Basic realm="{realm}"'}
    )

@app.route('/api/admin', methods=['GET'])
def admin_page():
    # Base64デコード
    auth = request.authorization
    if not auth or check_auth(auth.username, auth.password) != 'admin':
        return authenticate('Admin Area')
    return jsonify({"message": "Welcome to the Admin Area!"})

@app.route('/api/user', methods=['GET'])
def user_page():
    # Base64デコード
    auth = request.authorization
    if not auth or check_auth(auth.username, auth.password) != 'user':
        return authenticate('User Area')
    return jsonify({"message": "Welcome to the User Area!"})

# 認証情報がないため、必ず401となる。
@app.route('/api/products', methods=['GET'])
def products_page():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate('Products Area')
    return jsonify({"message": "Welcome to the Products Area!"})

if __name__ == "__main__":
    app.run(debug=True)