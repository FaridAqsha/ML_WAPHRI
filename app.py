import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
import bcrypt 
from werkzeug.security import generate_password_hash, check_password_hash
import pickle


app = Flask(__name__)
model = pickle.load(open("kchouse_model.pkl", "rb"))
app.secret_key = "membuatLOginFlask1"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route("/")
def home():
    return render_template('web.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM akun WHERE username=%s",(username,))
        user = curl.fetchone()
        curl.close()

        if user is not None and len(user) > 0 :
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['nama'] = user['nama']
                session['username'] = user['username']
                return redirect(url_for('home'))
            else :
                flash("Gagal, Username dan Password Tidak Cocok")
                return redirect(url_for('login'))
        else :
            flash("Gagal, Username Tidak Ditemukan")
            return redirect(url_for('login'))
    else: 
        return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else :
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO akun (nama,username,password) VALUES (%s,%s,%s)" ,(nama, username, hash_password)) 
        mysql.connection.commit()
        session['nama'] = request.form['nama']
        session['username'] = request.form['username']
        return redirect(url_for('login'))


@app.route("/predict", methods=["POST"])
def predict():
    float_features = [float(x) for x in request.form.values()]
    feature = [np.array(float_features)]
    prediction = model.predict(feature)
    return render_template("web.html", prediction_text = "{}".format(prediction))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login')) 

if __name__=="__main__":
    app.run(debug=True)