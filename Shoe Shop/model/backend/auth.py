from flask import Flask, render_template, redirect, url_for, request, flash, session
from db import mysql
from werkzeug.security import check_password_hash

def model_login():
  if request.method == 'POST':
    username = request.form['form_username']
    password = request.form['form_password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_admin WHERE username = %s", (username,))
    
    akun = cur.fetchone()
    if akun is None:
      flash("Gagal Login. Check username Anda", 'danger')
    # elif not check_password_hash(akun[2], password):
    elif password != akun[2]:
      flash("Gagal Login, Check password Anda.", 'danger')
    else:
      # Session: Menyimpan data, bisa sifat sementara.
      session['loggedin'] = True
      session['nama'] = akun[3]
      return redirect(url_for('dashboard'))
    
  return render_template('login_admin.html')

def model_logout():
  session.pop('loggedin', None)
  session.pop('nama', None)
  return redirect(url_for('login_admin'))
