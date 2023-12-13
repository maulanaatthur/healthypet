
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



app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('index.html')
    return render_template('index.html')
    

@app.route('/produk',methods=['GET' , 'POST'])
def produk():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('pesan_obat.html')
    return render_template('pesan_obat.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/forum")
def forum():
    return render_template('forum.html')

@app.route("/mulaikonsultasi")
def konsultasi():
    return render_template('artikel.html')

@app.route('/pesanan',methods=['GET' , 'POST'])
def pesanan():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('riwayat_obat.html')
    return render_template('riwayat_obat.html')

@app.route('/detail',methods=['GET' , 'POST'])
def detail():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('detail_pesan_obat.html')
    return render_template('detail_pesan_obat.html')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)