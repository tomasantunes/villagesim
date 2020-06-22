from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3
import datetime
import os

def connect_db():
	return sqlite3.connect("villagesim.db")

db = connect_db()

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "default_key"

def init():
	db = connect_db()
	c = db.cursor()

	sql_products_table = """ CREATE TABLE IF NOT EXISTS products (
							id integer PRIMARY KEY,
							name text,
                            price numeric,
                            daily_growth numeric,
							qtty numeric
						); """

	c.execute(sql_products_table)

	sql_users_table = """ CREATE TABLE IF NOT EXISTS users (
							id integer PRIMARY KEY,
							name text,
							balance text
						); """

	c.execute(sql_users_table)

def getProducts():
	db = connect_db()
	c = db.execute('SELECT * FROM products')
	rows = c.fetchall()
	return rows

@app.route("/add-product", methods=['POST'])
def addProduct():
	name = request.form.get('name', "")
	price = request.form.get('price', "")

	if (name != "" and price != ""):
		db = connect_db()
		db.execute('INSERT INTO products (name, price) VALUES (?, ?)', [name, price])
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"

@app.route("/")
def home():
    products = getProducts()
    return render_template('home.html', products=products)

if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=5000)