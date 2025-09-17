from flask import *
from datetime import datetime
import pymysql
import pandas as pd

app = Flask(__name__)

app.config['CON'] = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             database='Inventory',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    con = app.config['CON']
    cursor = con.cursor()
    products = "CREATE TABLE IF NOT EXISTS products(id INT AUTO_INCREMENT PRIMARY KEY, productName VARCHAR(255),\
    productNumber INT,startingInventory INT, inventoryReceived INT,inventoryShipped INT, inventoryOnHand INT,\
    minimumRequired INT DEFAULT '10',price INT)"

    supplier = "CREATE TABLE IF NOT EXISTS supplier(id INT AUTO_INCREMENT PRIMARY KEY, supplier VARCHAR(255))"

    orders = "CREATE TABLE IF NOT EXISTS orders(id INT AUTO_INCREMENT PRIMARY KEY, Title VARCHAR(255), \
    productId INT NOT NULL, numberShipped INT, orderDate DATE, FOREIGN KEY (productId) REFERENCES products(id))"

    purchases = "CREATE TABLE IF NOT EXISTS purchases(id INT AUTO_INCREMENT PRIMARY KEY, supplierId INT NOT NULL,\
    numberReceived INT,purchaseDate DATE,FOREIGN KEY (supplierId) REFERENCES supplier(id))"

    cursor.execute(products)
    con.commit()
    cursor.execute(supplier)
    con.commit()
    cursor.execute(purchases)
    con.commit()
    cursor.execute(orders)
    con.commit()

    cursor.execute('SELECT * FROM products')
    results = cursor.fetchall()
    cursor.execute('SELECT * FROM supplier')
    suppliers = cursor.fetchall()
    cursor.execute('SELECT SUM(inventoryOnHand) as available, SUM(inventoryReceived) as received,\
        SUM(inventoryShipped) as shipped, SUM(price) as price FROM products')
    available = cursor.fetchone()
    cursor.execute('SELECT COUNT(productName) as products FROM products')
    productcount = cursor.fetchone()
    cursor.execute('SELECT COUNT(supplier) as suppliers FROM supplier')
    supplierscount = cursor.fetchone()
    cursor.execute('SELECT COUNT(Title) as orders FROM orders')
    orderscount = cursor.fetchone()
    cursor.execute('SELECT COUNT(id) as purcheses FROM purchases')
    purchesescount = cursor.fetchone()

    return render_template("index.html", results = results, available=available,productcount=productcount,\
        supplierscount=supplierscount,orderscount=orderscount,purchesescount=purchesescount,suppliers=suppliers)

@app.route('/order/<int:pid>')
def order(pid):
    con = app.config['CON']
    cursor = con.cursor()
    cursor.execute('SELECT * FROM products where id = {}'.format(pid))
    results = cursor.fetchone()
    return render_template("order.html", results=results)
@app.route('/makeorder', methods=['POST'])
def makeorder():
    con = app.config['CON']
    cursor = con.cursor()
    if request.method == 'POST':
        pid = request.form['pid']
        amount = request.form['amount']
        inventoryOnHand = request.form['inventoryOnHand']
        inventoryShipped = request.form['inventoryShipped']
        newshipped = int(inventoryShipped) + int(amount)
        newonhand = int(inventoryOnHand) - int(amount)
        cursor.execute("UPDATE products SET inventoryShipped = {}, \
            inventoryOnHand = {} WHERE id = {}".format(newshipped,newonhand,pid))
        con.commit()
        return redirect('/')
@app.route('/addsupplier')
def addsupplier():
    return render_template('supplier.html')

@app.route('/supplier', methods=['POST'])
def supplier():
    con = app.config['CON']
    cursor = con.cursor()
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute("INSERT INTO supplier(supplier) VALUES ('{}')".format(name))
        con.commit()
        return redirect('/')
@app.route('/addproduct')
def addproduct():
    con = app.config['CON']
    cursor = con.cursor()
    cursor.execute('SELECT * FROM supplier')
    suppliers = cursor.fetchall()
    return render_template('product.html',suppliers = suppliers)

@app.route('/purchaseproduct', methods=['POST'])
def purchaseproduct():
    con = app.config['CON']
    cursor = con.cursor()
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        starting = request.form['starting']
        price = request.form['price']
        supplier = request.form['supplier']
        date = request.form['date']
        cursor.execute("INSERT INTO products(productName,productNumber,startingInventory,inventoryReceived\
            ,inventoryShipped,inventoryOnHand,price) VALUES ('{}','{}','{}','{}','{}','{}','{}'\
            )".format(name,number,starting,starting,0,starting,price))
        con.commit()
        cursor.execute("INSERT INTO purchases(supplierId,numberReceived,purchaseDate) VALUES ('{}','{}','{}'\
            )".format(supplier,starting,date))
        con.commit()

        return redirect('/')
@app.route('/manage/<int:pid>')
def manage(pid):
    con = app.config['CON']
    cursor = con.cursor()
    cursor.execute('SELECT * FROM products where id = {}'.format(pid))
    product = cursor.fetchone()
    cursor.execute('SELECT * FROM supplier')
    suppliers = cursor.fetchall()
    return render_template('manage.html', results = product, suppliers = suppliers)

@app.route('/manageproduct', methods=['POST'])
def manageproduct():
    con = app.config['CON']
    cursor = con.cursor()
    if request.method == 'POST':
        price = request.form['price']
        pid = request.form['id']
        inhand = request.form['inhand']
        supplier = request.form['supplier']
        received = request.form['received']
        date = request.form['date']
        newinhand = int(inhand) + int(received)
        cursor.execute("UPDATE products SET inventoryReceived = {}, price = {}\
            ,inventoryOnHand = {} WHERE id = {}".format(received,price,newinhand,pid))
        con.commit()
        cursor.execute("INSERT INTO purchases(supplierId,numberReceived,purchaseDate) VALUES ('{}','{}','{}'\
            )".format(supplier,inhand,date))
        con.commit()

        return redirect('/')