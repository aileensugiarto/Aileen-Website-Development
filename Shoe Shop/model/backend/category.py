from flask import Flask, render_template, redirect, url_for, request, flash
import os
from db import mysql


# Routing mengarah ke CATEGORY
def model_category():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_category")
  data = cur.fetchall()
  cur.close()
  return render_template('category/category.html', data_category=data)


# ADD CATEGORY
def model_add_category():
  # Add Data Category Process
  if request.method == "POST":
    category_name = request.form['form_name']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tbl_category VALUES (%s, %s)", ('', category_name))
    mysql.connection.commit()
    cur.close()

    flash("Data Successfully Added", 'success')
    return redirect(url_for('category'))
  # Jika if tidak terpenuhi
  return render_template('category/add_category.html')


# EDIT CATEGORY
def model_edit_category(id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM tbl_category WHERE id_category = %s", (id, ))
  data = cur.fetchone()
  return render_template('category/edit_category.html', data_category=data)


# PROCESS EDIT CATEGORY
def model_process_edit_category():
  category_name = request.form['form_name']
  id_category = request.form['form_id']
  cur = mysql.connection.cursor()
  cur.execute("UPDATE tbl_category SET category_name = %s WHERE id_category = %s", (category_name, id_category))
  mysql.connection.commit()
  cur.close()

  flash("Data Successfully Updated", 'success')
  return redirect(url_for('category'))


# DELETE CATEGORY
def model_delete_category(id):
  cur = mysql.connection.cursor()
  cur.execute("DELETE FROM tbl_category WHERE id_category = %s", (id, ))
  mysql.connection.commit()
  cur.close()

  flash("Data Successfully Deleted", 'danger')
  return redirect(url_for('category'))