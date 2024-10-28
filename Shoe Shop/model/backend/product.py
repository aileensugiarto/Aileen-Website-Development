from flask import Flask, render_template, redirect, url_for, request, flash
import os
from db import mysql

app = Flask(__name__)

# Untuk konfigurasi koneksi database
app.secret_key = 'aileen'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'


# Routing mengarah ke PRODUCT/BARANG
def get_category():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_category")
  categories = cur.fetchall()
  cur.close()
  return categories

# PRODUCT
def model_product():
  cur = mysql.connection.cursor()
  cur.execute("SELECT tbl_product.*, tbl_category.category_name FROM tbl_product JOIN tbl_category ON tbl_product.id_category = tbl_category.id_category ORDER BY tbl_product.id_product ASC")
  data = cur.fetchall() # menampilkan data
  cur.close()
  return render_template('product/product.html', data_product=data)

# ADD PRODUCT
def model_add_product():
  if request.method == "POST":
    product_name = request.form['form_product_name']
    id_category = request.form['form_id_category']
    price = request.form['form_price']
    description = request.form['form_description']
    product_stock = request.form['form_product_stock']

    # Untuk menambahkan gambar
    file = request.files['form_image']
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tbl_product (product_name, id_category, product_price, description, product_stock, image) VALUES (%s, %s, %s, %s, %s, %s)", (product_name, id_category, price, description, product_stock, [filename]))
    mysql.connection.commit() # update, delete, insert
    cur.close()
    return redirect(url_for('product'))
  return render_template('product/add_product.html', category=get_category())

# EDIT PRODUCT
def model_edit_product(id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_product WHERE id_product = %s", (id, ))
  data = cur.fetchone()
  return render_template('product/edit_product.html', data_product=data, category=get_category())

# PROCESS EDIT PRODUCT
def model_process_edit_product():
  product_name = request.form['form_product_name']
  price = request.form['form_price']
  description = request.form['form_description']
  product_stock = request.form['form_product_stock']
  id_product = request.form['form_id_product']
  id_category = request.form['form_id_category']
  # gambar = request.form['form_gambar']

  cur = mysql.connection.cursor()
  cur.execute("UPDATE tbl_product SET product_name = %s, id_category = %s, description = %s, product_price = %s, product_stock = %s WHERE id_product = %s", 
              (product_name, id_category, description, price, product_stock, id_product))
  mysql.connection.commit()

  file = request.files['form_image']
  filename = file.filename

  if file and filename != '':
    cur = mysql.connection.cursor()
    # Delete Old Image
    cur.execute("SELECT * FROM tbl_product WHERE id_product = %s", (id_product,))
    data = cur.fetchone()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], data[6]))

  # Update New Image
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cur.execute("UPDATE tbl_product SET image = %s WHERE id_product = %s", (filename, id_product))
    mysql.connection.commit()

  cur.close()

  flash("Data Successfully Updated", 'success')
  return redirect(url_for('product'))

# DELETE PRODUCT
def model_delete_product(id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_product WHERE id_product = %s", (id, ))
  data = cur.fetchone()
  os.remove(os.path.join(app.config['UPLOAD_FOLDER'], data[6]))
  cur.execute("DELETE FROM tbl_product WHERE id_product = %s", (id, ))
  mysql.connection.commit()
  cur.close()

  flash("Data Successfully Deleted", 'danger')
  return redirect(url_for('product'))