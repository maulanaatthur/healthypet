
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "SPARTA"

MONGODB_CONNECTION_STRING = "mongodb+srv://molware911:Almulki12@cluster0.zqmrb50.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbsparta_finalproject

TOKEN_KEY = 'mytoken'


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired!'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))


@app.route("/login", methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)


@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # id
        "password": password_hash,                                  # password
        # user's name is set to their id by default
        "profile_name": username_receive,
        # profile image file name
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # a default profile image
        # a profile description
        "profile_info": "",
        "access": 1
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/produk', methods=['GET', 'POST'])
def produk():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('pesan_obat.html')
    return render_template('pesan_obat.html')

@app.route('/produk_admin', methods=['GET', 'POST'])
def produk_admin():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('pesan_obat_admin.html')
    return render_template('pesan_obat_admin.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/forum")
def forum():
    return render_template('forum.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')


@app.route("/mulaikonsultasi")
def konsultasi():
    return render_template('artikel.html')


@app.route('/pesanan', methods=['GET', 'POST'])
def pesanan():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('riwayat_obat.html')
    return render_template('riwayat_obat.html')


@app.route('/detail', methods=['GET', 'POST'])
def detail():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('detail_pesan_obat.html')
    return render_template('detail_pesan_obat.html')


if __name__ == '__main__':
    # DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0', port=5000, debug=True)
