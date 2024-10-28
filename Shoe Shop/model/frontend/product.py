from flask import Flask, render_template, redirect, url_for, request, flash
import os
from db import mysql

def model_show_category():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_category")
  categories = cur.fetchall()
  cur.close()
  return categories

def model_show_product():
  cur = mysql.connection.cursor()
  cur.execute("SELECT tbl_product.*, tbl_category.category_name FROM tbl_product JOIN tbl_category ON tbl_product.id_category = tbl_category.id_category ORDER BY tbl_product.id_product ASC")
  data = cur.fetchall()
  cur.close()
  return data