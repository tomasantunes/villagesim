from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3
from datetime import datetime
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

	sql_requests_table = """ CREATE TABLE IF NOT EXISTS requests (
							id integer PRIMARY KEY,
							user_id integer,
							product_id integer,
							qtty numeric
						); """

	c.execute(sql_requests_table)

	sql_logs_table = """ CREATE TABLE IF NOT EXISTS logs (
							id integer PRIMARY KEY,
							user_id integer,
							date text,
							content text
						); """

	c.execute(sql_logs_table)

def getUserID(user):
	db = connect_db()
	c = db.execute('SELECT id FROM users WHERE name = ?', (user,))
	user_id = c.fetchall()[0][0]
	return user_id

def getProductID(product):
	db = connect_db()
	c = db.execute('SELECT id FROM products WHERE name = ?', (product,))
	product_id = c.fetchall()[0][0]
	return product_id

def getUserByID(id):
	db = connect_db()
	c = db.execute('SELECT * FROM users WHERE id = ?', (id,))
	user = c.fetchall()[0]
	return user

def getProductByID(id):
	db = connect_db()
	c = db.execute('SELECT * FROM products WHERE id = ?', (id,))
	product = c.fetchall()[0]
	return product

def getProducts():
	db = connect_db()
	c = db.execute('SELECT * FROM products')
	rows = c.fetchall()
	return rows

def getUsers():
	db = connect_db()
	c = db.execute('SELECT * FROM users')
	rows = c.fetchall()
	return rows

def getLogs():
	db = connect_db()
	c = db.execute('SELECT * FROM logs')
	rows = c.fetchall()
	return rows

def getRequests():
	db = connect_db()
	c = db.execute('SELECT * FROM requests')
	rows = c.fetchall()

	requests = []

	for row in rows:
		user = getUserByID(row[1])
		product = getProductByID(row[2])
		request = {
			'id': row[0],
			'user': user[1],
			'product' : product[1],
			'qtty' : row[3],
		}

		requests.append(request)
	
	return requests

def getTop10Products():
	db = connect_db()
	c = db.execute('SELECT p.name, p.price, SUM(r.qtty) FROM products p, requests r WHERE p.id = r.product_id GROUP BY p.id ORDER BY SUM(r.qtty) DESC LIMIT 10')
	rows = c.fetchall()
	return rows

@app.route("/add-product", methods=['POST'])
def addProduct():
	name = request.form.get('name', "")
	price = request.form.get('price', "")
	daily_growth = request.form.get('daily_growth', "")
	qtty = request.form.get('qtty', "")

	if (name != "" and price != "" and daily_growth != "" and qtty != ""):
		db = connect_db()
		db.execute('INSERT INTO products (name, price, daily_growth, qtty) VALUES (?, ?, ?, ?)', [name, price, daily_growth, qtty])
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"

@app.route("/add-user", methods=['POST'])
def addUser():
	name = request.form.get('name', "")
	balance = request.form.get('balance', "")

	if (name != "" and balance != ""):
		db = connect_db()
		db.execute('INSERT INTO users (name, balance) VALUES (?, ?)', [name, balance])
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"

@app.route("/new-request", methods=['POST'])
def newRequest():
	user = request.form.get('user', "")
	product = request.form.get('product', "")
	qtty = request.form.get('qtty', "")

	if (user != "" and product != "" and qtty != ""):
		db = connect_db()
		
		user_id = getUserID(user)
		product_id = getProductID(product)

		db.execute('INSERT INTO requests (user_id, date, entry) VALUES (?, ?, ?)', [user_id, date, entry])
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"

@app.route("/add-log-entry", methods=['POST'])
def addLogEntry():
	user = request.form.get('user', "")
	entry = request.form.get('entry', "")

	now = datetime.now()
	date = now.strftime("%d/%m/%Y %H:%M:%S")

	if (user != "" and entry != ""):
		db = connect_db()
		
		user_id = getUserID(user)

		db.execute('INSERT INTO logs (user_id, date, content) VALUES (?, ?, ?)', [user_id, date, entry])
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/products")
def products():
	products = getProducts()
	requests = getRequests()
	return render_template('products.html', products=products, requests=requests)

@app.route("/users")
def users():
	users = getUsers()
	return render_template('users.html', users=users)

@app.route("/stats")
def stats():
	top10products = getTop10Products()
	return render_template('stats.html', top10products=top10products)

@app.route("/logs")
def logs():
	logs = getLogs()
	return render_template('logs.html', logs=logs)

if __name__ == "__main__":
	init()
	app.run(host='0.0.0.0', port=5000)