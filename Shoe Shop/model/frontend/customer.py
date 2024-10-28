from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import os, requests, midtransclient, uuid
from db import mysql
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'aileen'
app.config['UPLOAD_FOLDER'] = 'static/uploads/bukti'

# Rajaongkir untuk pengiriman
RAJAONGKIR_API_KEY = '71bd102318358b6da806fe670361d8e3'
RAJAONGKIR_BASE_URL = 'https://api.rajaongkir.com/starter/'

# Midtrans untuk pembayaran
MIDTRANS_SERVER_KEY = 'SB-Mid-server-w0ErRPEwePcbBVB6qPKvhf7S'
MIDTRANS_CLIENT_KEY = 'SB-Mid-client-JxQrX9gXfnlck4zD'

# REGISTER CUSTOMER
def model_register_customer():
  if request.method == 'POST':
    username = request.form['form_username']
    password = request.form['form_password']
    name = request.form['form_name']
    age = request.form['form_age']
    telp = request.form['form_telp']
    address = request.form['form_address']
    email = request.form['form_email']
    cur = mysql.connection.cursor()

    # Check username
    cur.execute("SELECT * FROM tbl_customer WHERE username = %s", (username,))
    akun = cur.fetchone()
    
    if akun is None:
      # cur.execute("INSERT INTO tbl_customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", ('', username, generate_password_hash(password), nama, umur, telp, alamat, email))
      cur.execute("INSERT INTO tbl_customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", ('', username, password, name, age, telp, address, email))
      mysql.connection.commit()
      flash("Register Successfull", 'success')
      return redirect(url_for('login'))
    
    else:
      flash("Username Already Exists", 'danger')
      return redirect(url_for('register'))
      
  return render_template('frontend/register.html')


# LOGIN CUSTOMER
def model_login_customer():
  if request.method == 'POST':
    username = request.form['form_username']
    password = request.form['form_password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_customer WHERE username = %s", (username,))
    
    akun = cur.fetchone()
    if akun is None:
      flash("Login Failed. Check Your Username", 'danger')
    # elif not check_password_hash(akun[2], password):
    elif password != akun[2]:
      flash("Login Failed, Check Your Password.", 'danger')
    else:
      # Session: Menyimpan data, bisa sifat sementara.
      session['login'] = True
      session['name'] = akun[3]
      session['id_customer'] = akun[0]
      # redirect: mengarah ke route
      return redirect(url_for('index'))
  # render_template: .htmla
  return render_template('frontend/login.html')


# LOGOUT CUSTOMER
def model_logout_customer():
  session.pop('loggedin', None)
  session.pop('name', None)
  return redirect(url_for('login'))


# ADD TO CART
def model_add_cart():
  if request.method == "POST":
    id_customer = request.form['form_id_customer']
    id_product = request.form['form_id_product']
    price = request.form['form_price']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tbl_cart VALUES (%s, %s, %s, %s, %s)", ('', id_customer, id_product, 1, price))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('cart', id_customer=id_customer))
  # Jika if tidak terpenuhi
  return render_template('frontend/index.html')

# CART
def model_cart(id_customer):
  cur = mysql.connection.cursor()
  cur.execute("SELECT a.id_cart, a.qty, c.* FROM tbl_cart a JOIN tbl_customer b ON a.id_customer = b.id_customer JOIN tbl_product c ON a.id_product = c.id_product WHERE a.id_customer = %s", (id_customer,))
  data = cur.fetchall()
  cur.execute("SELECT SUM(price) FROM tbl_cart WHERE id_customer = %s", (id_customer,))
  total = cur.fetchone()[0]
  return render_template('frontend/cart.html', data_cart=data, total_price=total)

# UPDATE CART
def model_update_cart():
  id_cart = request.form['form_id_cart']
  id_product = request.form['form_id_product']
  price = request.form['form_price']
  qty = request.form['form_qty']
  id_customer = request.form['form_id_customer']
  # gambar = request.form['form_gambar']
  cur = mysql.connection.cursor()

  if 'plus' in request.form:
    qty_new = int(qty) + 1
    price_new = qty_new * int(price)
    cur.execute("UPDATE tbl_cart SET price = %s, qty = %s WHERE id_cart = %s", (price_new, qty_new, id_cart))
  else:
    if int(qty) == 1:
      return redirect(url_for('cart', id_customer=id_customer))
    else:
      qty_new = int(qty) - 1
      price_new = qty_new * int(price)
      cur.execute("UPDATE tbl_cart SET price = %s, qty = %s WHERE id_cart = %s", (price_new, qty_new, id_cart))

  mysql.connection.commit()

  return redirect(url_for('cart', id_customer=id_customer))


# DELETE CART
def model_delete_cart(id_cart):
  cur = mysql.connection.cursor()
  cur.execute("DELETE FROM tbl_cart WHERE id_cart = %s", (id_cart, ))
  mysql.connection.commit()
  cur.close()

  flash("Item Successfully Deleted", 'danger')
  return redirect(url_for('cart', id_customer=session['id_customer']))


# CHECKOUT
def get_provinces():
  url = f"{RAJAONGKIR_BASE_URL}province"
  headers = {'key': RAJAONGKIR_API_KEY}
  response = requests.get(url, headers=headers)
  data = response.json()
  if 'rajaongkir' in data and 'results' in data['rajaongkir']:
    return data['rajaongkir']['results']
  else:
    print(f'Error fetching provinces: {data}')
    return []

def model_checkout(id_customer):
  cur = mysql.connection.cursor()
  cur.execute("SELECT a.id_cart, a.qty, c.* FROM tbl_cart a JOIN tbl_customer b ON a.id_customer = b.id_customer JOIN tbl_product c ON a.id_product = c.id_product WHERE a.id_customer = %s", (id_customer,))
  data = cur.fetchall()
  cur.execute("SELECT SUM(price) FROM tbl_cart WHERE id_customer = %s", (id_customer,))
  total = cur.fetchone()[0]
  provinces = get_provinces()
  return render_template('frontend/checkout.html', data_cart=data, total_price=total, provinces=provinces)

# PROCESS CHECKOUT
def model_process_checkout():
  id_customer = request.form['form_id_customer']
  total_price = request.form['final_total_price_display']
  information = request.form['form_information']
  transaction_date = datetime.now().strftime("%Y-%m-%d")
  province = request.form['province']
  city = request.form['city']
  courier = request.form['courier']
  cur = mysql.connection.cursor()
  cur.execute("INSERT INTO tbl_payment_transaction VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", ('', id_customer, information, 'billing', transaction_date, total_price, province, city, courier))
  mysql.connection.commit()

  id_transaction = cur.lastrowid
  id_products = request.form.getlist('form_id_product[]')
  id_qty = request.form.getlist('form_qty[]')
  id_price = request.form.getlist('form_price[]')

  # for id_barang, qty, harga in zip(id_barangs, id_qty, id_harga):
  for product, qty, price in zip(id_products, id_qty, id_price): # zip: mengkelompokan id_barangs, id_qty, id_harga
    cur.execute("INSERT INTO tbl_payment_transaction_detail VALUES (%s, %s, %s, %s, %s)", ('', id_transaction, product, qty, price))
  mysql.connection.commit()

  id_carts = request.form.getlist('form_id_cart[]')
  for id_cart in id_carts:
    cur.execute("DELETE FROM tbl_cart WHERE id_cart = %s", (id_cart, ))
  mysql.connection.commit()

  cur.close()
  return redirect(url_for('order', id_customer=session['id_customer']))


# ORDER
def model_order(id_customer):
  # keterangan = request.form["form_keterangan"]
  # tanggal_transaksi = request.form["form_tanggal_transaksi"]
  # total_harga = request.form["total_harga"]
  # tanggal_transaksi = datetime.now().strftime("%Y-%m-%d")
  cur = mysql.connection.cursor()
  cur.execute("SELECT information, transaction_date, total_price, order_status, id_transaction FROM tbl_payment_transaction WHERE order_status = 'billing' AND id_customer = %s", (id_customer,))
  data = cur.fetchall()
  cur.execute("SELECT information, transaction_date, total_price, order_status, id_transaction FROM tbl_payment_transaction WHERE order_status = 'packing' AND id_customer = %s", (id_customer,))
  data_packaging = cur.fetchall()
  cur.execute("SELECT information, transaction_date, total_price, order_status, id_transaction FROM tbl_payment_transaction WHERE order_status = 'delivery' AND id_customer = %s", (id_customer,))
  data_delivery = cur.fetchall()
  cur.execute("SELECT information, transaction_date, total_price, order_status, id_transaction FROM tbl_payment_transaction WHERE order_status = 'sent' AND id_customer = %s", (id_customer,))
  data_sent = cur.fetchall()
  cur.close()
  return render_template('frontend/order.html', data_transaction_billing=data, data_transaction_packaging=data_packaging, data_transaction_delivery=data_delivery, data_transaction_sent=data_sent)


def model_billing():
  # Untuk menambahkan gambar
    # file = request.files['form_image']
    # filename = file.filename
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    transaction_id = request.form['form_id_transaction']
    total_price = request.form['form_total_price']

    snap = midtransclient.Snap(
      is_production=False,
      # Midtrans buat pembayaran
      server_key=MIDTRANS_SERVER_KEY,
      client_key=MIDTRANS_CLIENT_KEY
    )

    cur = mysql.connection.cursor()
    cur.execute("SELECT a.id_product, a.qty, a.price, tbl_product.product_name from tbl_payment_transaction_detail a JOIN tbl_product on a.id_product = tbl_product.id_product WHERE a.id_transaction = %s", [transaction_id])
    items = cur.fetchall()
    item_details = []
    for item in items:
      # product_name, price, qty, id_product = item
      item_details.append({
        "id": item[0],
        "price": int(item[2]),
        "quantity": int(item[1]),
        "name": item[3]
      })

      unique_order_id = f"{transaction_id}_{uuid.uuid4()}"

    param = {
      "transaction_details": {
      "order_id": unique_order_id,
      "gross_amount": int(total_price)
      },
      "item_details": item_details,
      "credit_card": {
        "secure": True
      },
      "customer_details": {
        "first_name": 'Anonymous',
        "last_name": '',
        "email": 'customer@gmail.com',
        "phone": '0912309834'
      }
    }
    transaction = snap.create_transaction(param)
    transaction_token = transaction['token']

    return jsonify({'token': transaction_token, 'transaction_id': transaction_id, 'total_price': total_price})

    # print("File: ") 
    # print(file) 
    # print("Filename: ", filename) 
    # print("Transaction ID: ", transaction_id) 
    # print("Total Price: ", total_price)

    # cur = mysql.connection.cursor()
    # cur.execute("INSERT INTO tbl_payment VALUES (%s, %s, %s, %s, %s, %s)", ('', transaction_id, total_price, 'paid', 'transfer', [filename]))
    
    # mysql.connection.commit()

    # cur.execute("UPDATE tbl_payment_transaction SET order_status = %s WHERE id_transaction = %s", 
    #           ('packing', transaction_id))
    
    # mysql.connection.commit()

    # cur.close()
    # return redirect(url_for('order', id_customer=session['id_customer']))

# SAVE PAYMENT INFO
def model_save_payment_info():
  try:
    data = request.get_json()
    transaction_id = data['transaction_id']
    total_price = data['total_price']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO tbl_payment (id_transaction, total_payment, payment_status, payment_method) VALUES (%s, %s, %s, %s)", 
        (transaction_id, total_price, 'paid', 'transfer')
    )

    mysql.connection.commit()

    # Update tbl_payment_transaction table
    cur.execute(
        "UPDATE tbl_payment_transaction SET order_status = %s WHERE id_transaction = %s", 
        ('packing', transaction_id)
    )

    mysql.connection.commit()

    cur.close()
    return jsonify({'status': 'success'})
  except Exception as e:
    print('Error occured: ', e)
    return jsonify({'error': str(e)}), 500

# PROCESS SENT
def model_process_sent():
  transaction_id = request.form['form_id_transaction']
  print(transaction_id)
  cur = mysql.connection.cursor()
  cur.execute("UPDATE tbl_payment_transaction SET order_status = %s WHERE id_transaction = %s", ('sent', transaction_id))
  mysql.connection.commit()

  cur.close()
  return redirect(url_for('order', id_customer=session['id_customer']))




# Payment process (using Midtrans Snap)
@app.route('/payment', methods=['POST'])
def payment():
    if 'login' in session:
        id_customer = session['id_customer']
        total_price = float(request.form['total_price'])  # Ensure total_price is a float
        customer_name = session['name']

        # Prepare transaction data for Midtrans
        transaction = {
            'transaction_details': {
                'order_id': f'order-{id_customer}-{session["name"]}',  # Unique order ID
                'gross_amount': total_price
            },
            'customer_details': {
                'first_name': customer_name,
                'email': session.get('email', 'example@example.com')  # Replace with customer's email if available
            },
            'item_details': [
                {
                    'id': 'item1',
                    'price': total_price,
                    'quantity': 1,
                    'name': 'Total Cart Payment'
                }
            ]
        }

        # Create transaction with Midtrans
        try:
            snap_token = snap.create_transaction(transaction)['token']
            return render_template('payment.html', snap_token=snap_token)
        except Exception as e:
            print("Midtrans error:", e)  # Log the error
            return "An error occurred while processing payment."

    else:
        return redirect(url_for('login_customer'))
