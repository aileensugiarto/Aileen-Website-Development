from flask import Flask, render_template, redirect, url_for, request, flash
import os
from db import mysql


# Routing mengarah ke TRANSAKSI
def model_transaction():
  # cur = mysql.connection.cursor()
  # cur.execute("SELECT a.*, b.name  FROM tbl_payment_transaction a JOIN tbl_customer b ON a.id_customer = b.id_customer")
  # data = cur.fetchall()
  # cur.close()
  cur = mysql.connection.cursor()
  cur.execute("SELECT a.*, b.name  FROM tbl_payment_transaction a JOIN tbl_customer b ON a.id_customer = b.id_customer WHERE a.order_status = 'billing'")
  data = cur.fetchall()

  cur.execute("SELECT a.*, b.name  FROM tbl_payment_transaction a JOIN tbl_customer b ON a.id_customer = b.id_customer WHERE a.order_status = 'packing'")
  data_packaging = cur.fetchall()

  cur.execute("SELECT a.*, b.name  FROM tbl_payment_transaction a JOIN tbl_customer b ON a.id_customer = b.id_customer WHERE a.order_status = 'delivery'")
  data_delivery = cur.fetchall()

  cur.execute("SELECT a.*, b.name  FROM tbl_payment_transaction a JOIN tbl_customer b ON a.id_customer = b.id_customer WHERE a.order_status = 'sent'")
  data_sent = cur.fetchall()
  cur.close()
  
  return render_template('transaction/transaction.html', data_transaction_billing=data, data_transaction_packaging=data_packaging, data_transaction_delivery=data_delivery, data_transaction_sent=data_sent)

# PROCESS DELIVERY
def model_process_delivery():
  transaction_id = request.form['form_id_transaction']
  cur = mysql.connection.cursor()
  cur.execute("UPDATE tbl_payment_transaction SET order_status = %s WHERE id_transaction = %s", ('delivery', transaction_id))
  mysql.connection.commit()

  cur.close()
  return redirect(url_for('transaction'))

# DETAIL TRANSACTION
def model_detail_transaction(transaction_id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT a.*, b.province_name, c.city_name FROM tbl_payment_transaction a JOIN tbl_provinces b ON a.province = b.province_id JOIN tbl_cities c ON a.city = c.city_id WHERE id_transaction = %s", [transaction_id])
  data_transaction = cur.fetchone()
  mysql.connection.commit()

  cur.execute("SELECT b.*  FROM tbl_payment_transaction a JOIN tbl_customer b ON a.id_customer = b.id_customer WHERE id_transaction = %s", [transaction_id])
  data_customer = cur.fetchone()
  mysql.connection.commit()

  cur.execute("SELECT a.id_product, a.qty, a.price, tbl_product.product_name from tbl_payment_transaction_detail a JOIN tbl_product on a.id_product = tbl_product.id_product WHERE a.id_transaction = %s", [transaction_id])
  data_product = cur.fetchall()
  mysql.connection.commit()

  cur.execute("SELECT total_price FROM tbl_payment_transaction WHERE id_transaction = %s", [transaction_id])
  total = cur.fetchone()[0]
  mysql.connection.commit()

  cur.close()
  return render_template('transaction/detail_transaction.html', data_product=data_product, data_transaction=data_transaction, total_price=total, data_customer=data_customer)