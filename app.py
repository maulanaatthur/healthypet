from flask import Flask,redirect,url_for,render_template,request
from pymongo import MongoClient




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

@app.route("/mulaikonsultasi")
def konsultasi():
    return render_template('artikel.html')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)