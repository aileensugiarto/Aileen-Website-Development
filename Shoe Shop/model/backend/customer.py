from flask import Flask, render_template, redirect, url_for, request, flash
import os
from db import mysql


# Routing mengarah ke CUSTOMER
def model_customer():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_customer")
  data = cur.fetchall()
  cur.close()
  return render_template('customer/customer.html', data_customer=data)

# TAMBAH CUSTOMER
def model_add_customer():
  # Process tambah data
  if request.method == "POST":
    customer_name = request.form['form_customer_name']
    customer_age = request.form['form_customer_age']
    customer_telp = request.form['form_customer_telp']
    customer_address = request.form["form_customer_address"]
    customer_email = request.form["form_customer_email"]
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tbl_customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", ('', '', '', customer_name, customer_age, customer_telp, customer_address, customer_email))
    mysql.connection.commit()
    cur.close()

    flash("Data Successfully Added", 'success')
    return redirect(url_for('customer'))
  # Jika if tidak terpenuhi
  return render_template('customer/add_customer.html')

# EDIT CUSTOMER
def model_edit_customer(id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_customer WHERE id_customer = %s", (id, ))
  data = cur.fetchone()
  return render_template('customer/edit_customer.html', data_customer=data)

# PROCESS EDIT CUSTOMER
def model_process_edit_customer():
  id_customer = request.form['form_id_customer']
  customer_name = request.form['form_customer_name']
  customer_age = request.form['form_customer_age']
  customer_telp = request.form['form_customer_telp']
  customer_address = request.form["form_customer_address"]
  customer_email = request.form["form_customer_email"]
  cur = mysql.connection.cursor()
  cur.execute("UPDATE tbl_customer SET name = %s, age = %s, telp = %s, address = %s, email = %s WHERE id_customer = %s", (customer_name, customer_age, customer_telp, customer_address, customer_email, id_customer))
  mysql.connection.commit()
  cur.close()

  flash("Data Successfully Updated", 'success')
  return redirect(url_for('customer'))

# DELETE CUSTOMER
def model_delete_customer(id):
  cur = mysql.connection.cursor()
  cur.execute("DELETE FROM tbl_customer WHERE id_customer = %s", (id, ))
  mysql.connection.commit()
  cur.close()

  flash("Data Successfully Deleted", 'danger')
  return redirect(url_for('customer'))