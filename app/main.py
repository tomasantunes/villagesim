from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3
from datetime import datetime
import os
import random

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
							balance numeric,
							total_spent numeric DEFAULT 0,
							monthly_income numeric DEFAULT 0
						); """

	c.execute(sql_users_table)

	sql_jobs_table = """ CREATE TABLE IF NOT EXISTS jobs (
							id integer PRIMARY KEY,
							user_id integer,
							title text,
							salary numeric
						); """

	c.execute(sql_jobs_table)

	sql_requests_table = """ CREATE TABLE IF NOT EXISTS requests (
							id integer PRIMARY KEY,
							user_id integer,
							product_id integer,
							qtty numeric,
							recurrent integer,
							date text,
							total numeric
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
	rows = c.fetchall()
	if len(rows) > 0:
		user_id = rows[0][0]
		return user_id
	else:
		return False

@app.route("/generate-users", methods=['POST'])
def generateUsers():
	qtty = request.form.get('qtty', "")
	print(qtty)
	print("x1")
	if (qtty != ""):
		for i in range(0, int(qtty)):
			name = random.choice(open('static/usernames.txt', encoding="utf-8").readlines())
			r = random.random()
			if (r < 0.01):
				balance = round(random.uniform(2.50, 100000.00), 2)
			elif (r < 0.10):
				balance = round(random.uniform(2.50, 10000.00), 2)
			else:
				balance = round(random.uniform(2.50, 1000.00), 2)
			db = connect_db()
			db.execute('INSERT INTO users (name, balance) VALUES (?, ?)', [name, balance])
			db.commit()
		print("x2")
		return redirect("/users")
	else:
		return "Submission Invalid"

def getProduct(product):
	db = connect_db()
	c = db.execute('SELECT * FROM products WHERE name = ?', (product,))
	rows = c.fetchall()
	if len(rows) > 0:
		product = rows[0]
		return product
	else:
		return False

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
	users = []

	for row in rows:
		c = db.execute('SELECT total FROM requests WHERE user_id = ? AND recurrent = 1', (row[0],))
		total = c.fetchall()
		print(row[4])
		user = {
			'id': row[0],
			'name': row[1],
			'balance' : row[2],
			'monthly_expense' : 0,
			'total_spent' : round(row[3], 2),
			'monthly_income' : row[4],
		}

		if len(total) > 0:
			t = 0
			for i in total:
				t += i[0]
			user['monthly_expense'] = round(t, 2)

		users.append(user)
	return users

def getLogs():
	db = connect_db()
	c = db.execute('SELECT * FROM logs')
	rows = c.fetchall()
	return rows

def getJobs():
	db = connect_db()
	c = db.execute('SELECT * FROM jobs')
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
			'date' : row[5],
			'total' : round(row[6], 2),
			'recurrent' : "true" if row[4] == 1 else "false",
		}

		requests.append(request)
	
	return requests

def getBankMonthlyIncome():
	db = connect_db()
	c = db.execute('SELECT SUM(total) FROM requests WHERE recurrent = 1')
	income = c.fetchall()[0][0]
	if income == None:
		income = 0
	else:
		income = round(income, 2)
	return income

def getTop10Products():
	db = connect_db()
	c = db.execute('SELECT p.name, p.price, SUM(r.qtty) FROM products p, requests r WHERE p.id = r.product_id GROUP BY p.id ORDER BY SUM(r.qtty) DESC LIMIT 10')
	rows = c.fetchall()
	return rows

def getTop10Users():
	db = connect_db()
	c = db.execute('SELECT name, total_spent FROM users ORDER BY total_spent DESC LIMIT 10')
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
		return redirect("/shop")
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
		return redirect("/users")
	else:
		return "Submission Invalid"

@app.route("/new-request", methods=['POST'])
def newRequest():
	user = request.form.get('user', "")
	product = request.form.get('product', "")
	qtty = request.form.get('qtty', "")
	recurrent = request.form.get('recurrent', "")

	recurrent = True if recurrent == "on" else False

	user_id = getUserID(user)
	product = getProduct(product)

	if (user_id != False and product != False and qtty != ""):
		db = connect_db()

		now = datetime.now()
		date = now.strftime("%d/%m/%Y %H:%M:%S")
		total = round(int(qtty) * product[2], 2)

		db.execute('INSERT INTO requests (user_id, product_id, qtty, recurrent, date, total) VALUES (?, ?, ?, ?, ?, ?)', [user_id, product[0], qtty, recurrent, date, total])
		db.commit()
		if not recurrent:
			db.execute('UPDATE users SET total_spent = total_spent + ? WHERE id = ?', (total, user_id))
			db.commit()

		return redirect("/shop")
	else:
		return "Submission Invalid"

@app.route("/generate-requests", methods=['POST'])
def generateRequests():
	qtty = request.form.get('qtty', "")

	if (qtty != ""):
		products = getProducts()
		users = getUsers()

		for i in range(0, int(qtty)):
			qtty = random.randint(1, 100)
			recurrent = True if random.random() < 0.75 else False

			product = random.choice(products)
			user = random.choice(users)

			user_id = user['id']
			product_id = product[0]

			if (user_id != False and product != False and qtty != ""):
				db = connect_db()

				now = datetime.now()
				date = now.strftime("%d/%m/%Y %H:%M:%S")
				total = round(int(qtty) * product[2], 2)

				db.execute('INSERT INTO requests (user_id, product_id, qtty, recurrent, date, total) VALUES (?, ?, ?, ?, ?, ?)', [user_id, product_id, qtty, recurrent, date, total])
				db.commit()
				if not recurrent:
					db.execute('UPDATE users SET total_spent = total_spent + ? WHERE id = ?', (total, user_id))
					db.commit()

		return redirect("/shop")
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
		return redirect("/logs")
	else:
		return "Submission Invalid"

@app.route("/add-job", methods=['POST'])
def addJob():
	title = request.form.get('title', "")
	user = request.form.get('user', "")
	salary = request.form.get('salary', "")

	if (user != "" and title != "" and salary != ""):
		db = connect_db()
		
		user_id = getUserID(user)

		db.execute('INSERT INTO jobs (title, salary, user_id) VALUES (?, ?, ?)', [title, salary, user_id])
		db.commit()
		db.execute('UPDATE users SET monthly_income = ? WHERE id = ?', (salary, user_id))
		db.commit()
		return redirect("/human-resources")
	else:
		return "Submission Invalid"

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/shop")
def products():
	products = getProducts()
	requests = getRequests()
	return render_template('shop.html', products=products, requests=requests)

@app.route("/users")
def users():
	users = getUsers()
	return render_template('users.html', users=users)

@app.route("/stats")
def stats():
	top10products = getTop10Products()
	top10users = getTop10Users()
	return render_template('stats.html', top10products=top10products, top10users=top10users)

@app.route("/bank")
def bank():
	monthly_income = getBankMonthlyIncome()

	# TODO: Add monthly expense and waste

	return render_template('bank.html', monthly_income=monthly_income)

@app.route("/human-resources")
def humanResources():
	jobs = getJobs()
	return render_template('human-resources.html', jobs=jobs)

@app.route("/logs")
def logs():
	logs = getLogs()
	return render_template('logs.html', logs=logs)

if __name__ == "__main__":
	init()
	app.run(host='0.0.0.0', port=5000)