from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import os, requests
from db import mysql
from flask_mysqldb import MySQL

# Backend
from model.backend.auth import model_login, model_logout
from model.backend.customer import model_customer, model_add_customer, model_edit_customer, model_process_edit_customer, model_delete_customer
from model.backend.category import model_category, model_add_category, model_edit_category, model_process_edit_category, model_delete_category
from model.backend.product import model_product, model_add_product, model_edit_product, model_process_edit_product, model_delete_product
from model.backend.transaction import model_transaction, model_process_delivery, model_detail_transaction
from model.backend.payment import model_payment

# Frontend
from model.frontend.customer import model_login_customer, model_register_customer, model_logout_customer, model_cart, model_checkout, model_process_checkout, model_add_cart, model_update_cart, model_delete_cart, model_order, model_billing, model_save_payment_info, model_process_sent
from model.frontend.product import model_show_category, model_show_product

app = Flask(__name__)

app.secret_key = 'aileen'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Default XAMPP MySQL user
app.config['MYSQL_PASSWORD'] = ''  # Default XAMPP MySQL password (empty by default)
app.config['MYSQL_DB'] = 'shoe_shop'
app.config['MYSQL_PORT'] = 3306  # Default MySQL port in XAMPP
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

mysql.init_app(app)

RAJAONGKIR_API_KEY = '71bd102318358b6da806fe670361d8e3'
RAJAONGKIR_BASE_URL = 'https://api.rajaongkir.com/starter/'
ORIGIN_CITY_ID = '444'


# GET: dari url
# POST: langsung dari form


# FRONTEND START
@app.route('/')
def index():
  data_category = model_show_category()
  data_product = model_show_product()
  return render_template('frontend/index.html', category=data_category, product=data_product)

# REGISTER CUSTOMER
@app.route('/register', methods=['GET', 'POST'])
def register():
  return model_register_customer()

# LOGIN CUSTOMER
@app.route('/login', methods=['GET', 'POST'])
def login():
  return model_login_customer()

# LOGOUT CUSTOMER
@app.route('/logout')
def logout():
  return model_logout_customer()

# ADD TO CART
@app.route('/add_cart', methods=['GET', 'POST'])
def add_cart():
  return model_add_cart()

# CART
@app.route('/cart/<int:id_customer>', methods=['GET', 'POST'])
def cart(id_customer):
  return model_cart(id_customer)

# UPDATE CART
@app.route('/update_cart', methods=['GET', 'POST'])
def update_cart():
  return model_update_cart()

# DELETE CART
@app.route('/delete_cart/<int:id_cart>', methods=['GET'])
def delete_cart(id_cart):
  return model_delete_cart(id_cart)

# CITIES
@app.route('/get_cities/<province_id>', methods=['GET'])
def cities(province_id):
  url = f"{RAJAONGKIR_BASE_URL}city?province={province_id}"
  headers = {'key': RAJAONGKIR_API_KEY}
  response = requests.get(url, headers=headers)
  data = response.json()
  if 'rajaongkir' in data and 'results' in data['rajaongkir']:
    return jsonify(data['rajaongkir']['results'])
  else:
    return jsonify({'error': 'Unable to fetch cities', 'details': data})

# SHIPPING COST
@app.route('/get_shipping_cost', methods=['POST'])
def shipping_cost():
  origin = ORIGIN_CITY_ID
  destination = request.form['destination']
  weight = request.form['weight']
  courier = request.form['courier']
  url = f"{RAJAONGKIR_BASE_URL}cost"
  headers = {'key': RAJAONGKIR_API_KEY}
  data = {
    'origin': origin,
    'destination': destination,
    'weight': weight,
    'courier': courier
  }
  response = requests.post(url, headers=headers, data=data)
  data = response.json()
  if 'rajaongkir' in data and 'results' in data['rajaongkir']:
    return jsonify(data['rajaongkir']['results'])
  else:
    return jsonify({'error': 'Unable to fetch cities', 'details': data})

# CHECKOUT
@app.route('/checkout/<int:id_customer>', methods=['GET', 'POST'])
def checkout(id_customer):
  return model_checkout(id_customer)

# PROCESS CHECKOUT
@app.route('/process_checkout', methods=['GET', 'POST'])
def process_checkout():
  return model_process_checkout()

# ORDER
@app.route('/order/<int:id_customer>', methods=['GET'])
def order(id_customer):
  return model_order(id_customer)

# BILLING
@app.route('/billing', methods=['GET', 'POST'])
def billing():
  return model_billing()

# SAVE PAYMENT INFO
@app.route('/save_payment_info', methods=['POST'])
def save_payment_info():
  return model_save_payment_info()

# PROCESS SENT
@app.route('/sent', methods=['POST'])
def process_sent():
  return model_process_sent()

# BACKEND START

# Routing to LOGIN ADMIN
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
  return model_login()

# Routing to LOGOUT ADMIN
@app.route('/logout_admin')
def logout_admin():
  return model_logout()

# Routing to DASHBOARD
@app.route('/dashboard')
def dashboard():
  if "loggedin" in session:
    cur = mysql.connection.cursor()

    # Total Customer
    cur.execute("SELECT COUNT(id_customer) FROM tbl_customer")
    data_customer = cur.fetchone()[0]

    # Total Products
    cur.execute("SELECT COUNT(id_product) FROM tbl_product JOIN tbl_category ON tbl_product.id_category = tbl_category.id_category")
    data_product = cur.fetchone()[0]

    # Total Payment Transaction
    cur.execute("SELECT COUNT(id_transaction) FROM tbl_payment_transaction")
    data_transaction = cur.fetchone()[0]

    # Total Payment
    cur.execute("SELECT COUNT(id_payment) FROM tbl_payment")
    data_payment = cur.fetchone()[0]

    cur.close()

    return render_template('index_backend.html', total_customer=data_customer, total_product=data_product, total_transaction=data_transaction, total_payment=data_payment)

  flash('Please login.', 'danger')
  return redirect(url_for('login_admin'))


# CUSTOMER
@app.route('/customer')
def customer():
  return model_customer()

# ADD CUSTOMER
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
  return model_add_customer()

# EDIT CUSTOMER
@app.route('/edit_customer/<int:id>', methods=['GET'])
def edit_customer(id):
  return model_edit_customer(id)

# PROCESS EDIT CUSTOMER
@app.route('/process_edit_customer', methods=['POST'])
def process_edit_customer():
  return model_process_edit_customer()

# DELETE CUSTOMER
@app.route('/delete_customer/<int:id>', methods=['GET'])
def delete_customer(id):
  return model_delete_customer(id)


# CATEGORY
# Routing to CATEGORY
@app.route('/category')
def category():
  return model_category()

# ADD CATEGORY
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
  return model_add_category()

# EDIT CATEGORY
@app.route('/edit_category/<int:id>', methods=['GET'])
def edit_category(id):
  return model_edit_category(id)

# PROCESS EDIT CATEGORY
@app.route('/process_edit_category', methods=['POST'])
def process_edit_category():
  return model_process_edit_category()

# DELETE CATEGORY
@app.route('/delete_category/<int:id>', methods=['GET'])
def delete_category(id):
  return model_delete_category(id)


# PRODUCT
# Routing to PRODUCT
@app.route('/product')
def product():
  return model_product()

# ADD PRODUCT
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
  return model_add_product()

# EDIT PRODUCT
@app.route('/edit_product/<int:id>', methods=['GET'])
def edit_product(id):
  return model_edit_product(id)

# PROCESS EDIT PRODUCT
@app.route('/process_edit_product', methods=['POST'])
def process_edit_product():
  return model_process_edit_product()

# DELETE PRODUCT
@app.route('/delete_product/<int:id>', methods=['GET'])
def delete_product(id):
  return model_delete_product(id)


# SALES TRANSACTION
@app.route('/transaction')
def transaction():
  return model_transaction()


# PAYMENT
@app.route('/payment')
def payment():
  return model_payment()
# BACKEND END


if __name__ == '__main__':
  app.run(debug=True)