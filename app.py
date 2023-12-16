from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "SPARTA"

MONGODB_CONNECTION_STRING = "mongodb+srv://molware911:Almulki12@cluster0.zqmrb50.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbsparta_finalproject



app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256'],
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired!'
        return redirect(url_for('login', msg=msg))
    

@app.route("/login", methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route("/register")
def register():
    return render_template('register.html')


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
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        response = make_response(
            jsonify({"result": "success", "token": token}),
            200,
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5000"  # Sesuaikan dengan URL Anda
        response.headers["Set-Cookie"] = f"mytoken={token}; Path=/; HttpOnly; SameSite=None; Secure"
        
        return response
    else:
       return make_response(jsonify({"result": "fail", "msg": "Username/password combination not found"}), 401)


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nama_receive = request.form['nama_give']
    alamat_receive = request.form['alamat_give']
    nomorhp_receive = request.form['nomorhp_give']
    email_receive = request.form['email_give']
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # id
        "password": password_hash,                                  # password
        "nama" : nama_receive,
        "alamat" : alamat_receive,
        "nomorHp" : nomorhp_receive,
        "email" : email_receive,
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

@app.route("/posting", methods=['POST'])
def posting():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        comment_receive = request.form.get('comment_give')
        date_receive = request.form.get('date_give')
        doc = {
            'username': user_info.get('username'),
            'profile_name': user_info.get('profile_name'),
            'profile_pic_real': user_info.get('profile_pic_real'),
            'comment': comment_receive,
            'date': date_receive,
        }
        db.posts.insert_one(doc)
        return jsonify({
            'result': 'success',
            'msg': 'Posting successful!'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route("/get_posts", methods=["GET"])
def get_posts():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username_receive = request.args.get('username_give')
        if username_receive == '':
            posts = list(db.posts.find({}).sort("date", -1).limit(20))

        else:
            posts = list(db.posts.find(
                {'username': username_receive}).sort("date", -1).limit(20))
        # We should fetch the full list of posts here

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "heart"}
            )
            post["count_star"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "star"}
            )
            post["count_thumbsup"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "thumbsup"}
            )
            post["heart_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "heart",
                        "username": payload["id"]}
                )
            )
            post["star_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "star",
                        "username": payload["id"]}
                )
            )
            post["thumbsup_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "thumbsup",
                        "username": payload["id"]}
                )
            )
        return jsonify(
            {
                "result": "success",
                "msg": "Successful fetched all posts",
                "posts": posts,
            }
        )
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/update_like", methods=["POST"])
def update_like():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # We should change the like count for the post here
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive,
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents(
            {"post_id": post_id_receive, "type": type_receive}
        )
        return jsonify({"result": "success", "msg": "updated", "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/produk', methods=['GET', 'POST'])
def produk():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('pesan_obat.html')
    return render_template('pesan_obat.html')

@app.route('/detail_get', methods=['POST'])
def detail_get():
    id_receive = request.form.get('id_give')
    result = db.obat.find_one({'id': int(id_receive)})
    if result:
        return render_template(
            'detail_pesan_obat.html',
            result=result
        )

@app.route('/detail', methods=['GET'])
def detail_get():
    id_receive = request.form.get('id_give')
    result = db.obat.find_one({'id': int(id_receive)})
    if result:
        return render_template(
            'detail_pesan_obat.html',
            result=result
        )



@app.route("/delete", methods=["POST"])
def delete():
    id_receive = request.form.get('id_give')
    db.obat.delete_one(
        {'id' : int(id_receive) }
    )

@app.route('/produk_admin', methods=['GET', 'POST'])
def produk_admin():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('pesan_obat_admin.html')
    return render_template('pesan_obat_admin.html')

@app.route("/produk_admin_upload", methods=['GET'])
def show_product():
    articles = list(db.obat.find({},{'_id': False}))
    return jsonify({'articles' : articles})

@app.route('/produk_admin_upload', methods=['POST'])
def save_product():
    title_receive = request.form.get('title_give')
    cost_receive = request.form.get('cost_give')
    content_receive = request.form.get('content_give')
    
    file = request.files['file_give']
    extension = file.filename.split('.')[-1]
    filename = f'static/product/product-{title_receive}.{extension}'
    file.save(filename)
    count = db.obat.count_documents({})
    id= count + 1
    
    doc = {
        'id' : id,
        'file': filename,
        'title': title_receive,
        'cost': cost_receive,
        'content' : content_receive,
    }
    db.obat.insert_one(doc)
    return jsonify({'message' : 'data disimpan'})

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/forum")
def forum():
    return render_template('forum.html')


@app.route("/profile/<username>", methods=["GET"])
def user(username):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        status = username == payload.get("id")
        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template("profile.html", user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route("/update_profile", methods=["POST"])
def save_img():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        alamat_receive = request.form["alamat_give"]
        new_doc = {"profile_name": name_receive, "profile_info": about_receive , "alamat":alamat_receive}
        if "file_give" in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({"username": payload["id"]}, {"$set": new_doc})
        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route("/mulaikonsultasi")
def konsultasi():
    return render_template('artikel.html')


@app.route('/pesanan', methods=['GET', 'POST'])
def pesanan():
    if request.method == 'POST':
        # Handle POST Request here
        return render_template('riwayat_obat.html')
    return render_template('riwayat_obat.html')


# @app.route('/detaia', methods=['GET', 'POST'])
# def detail():
#     if request.method == 'POST':
#         # Handle POST Request here
#         return render_template('detail_pesan_obat.html')
#     return render_template('detail_pesan_obat.html')


if __name__ == '__main__':
    # DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0', port=5000, debug=True)
