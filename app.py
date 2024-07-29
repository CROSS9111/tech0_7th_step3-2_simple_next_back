from flask import Flask, request, jsonify
import crud, mymodels
import os

app = Flask(__name__)

test_location = [
    {"id": "test_user1", "latitude": 35.6895, "longitude": 139.6917},
    {"id": "test_user2", "latitude": 34.0522, "longitude": -118.2437}
]

@app.route("/")
def index():
    return "<p>Flask top page!</p>"

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

@app.route("/add", methods=["GET"])
def add():
    try:
        for loc in test_location:
            crud.myinsert(mymodels.Location, loc)
        return jsonify({"message": "Test locations added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/read", methods=["GET"])
def read():
    try:
        locations = crud.myload(mymodels.Location)
        locations_list = [{"id": loc.id, "latitude": loc.latitude, "longitude": loc.longitude} for loc in locations]
        return jsonify(locations_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == "__main__":
    app.run(debug=True)