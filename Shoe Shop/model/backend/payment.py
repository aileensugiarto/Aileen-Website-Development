from flask import Flask, render_template, redirect, url_for, request, flash
import os
from db import mysql


# Routing mengarah ke PEMBAYARAN
def model_payment():
  cur = mysql.connection.cursor()
  cur.execute("SELECT id_transaction, payment_method, payment_proof, total_payment, payment_status FROM tbl_payment")
  data = cur.fetchall()
  cur.close()
  return render_template('payment/payment.html', data_payment=data)