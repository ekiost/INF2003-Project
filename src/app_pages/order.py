from __main__ import app
from bson import ObjectId
from congoDB import create, read, update, delete
from flask import Flask, redirect, request, render_template, session, url_for
from controller.mongodbController import MongoDBController
from app_pages.cart import getCart, getProducts, getSubtotal
from app_pages.orders import setOrderStatus
from app_pages.cart import getCart, getProducts, getSubtotal, getProductDetails
import datetime

mgdb = MongoDBController()


def checkout(cart: dict, order_total: float):
    # if cart['products'] == []:
    #     print("Cart is empty")  
    #     return redirect(url_for('cart'))
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    arrival_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%d/%m/%Y")

    cart = getCart()
    products_to_checkout = getProducts(cart)
    order_total = getSubtotal(products_to_checkout)

    data = {
        'user_id': cart['user_id'],
        'products': products_to_checkout,
        'date': date,
        'status': 'pending',
        'arrival_date': arrival_date,
        'total': float(order_total)
    }

    for product in products_to_checkout:
        reduceProductStockFromOrder(product)

    _id = mgdb.create('Orders', data)
    mgdb.update('Cart', {'user_id': cart['user_id']}, {'products': []})
    #clear session cart
    session['cart'] = []
    #!!! REMEMBER TO IMPLEMENT THE UPDATE OF THE PRODUCT STOCK
    
    return _id.inserted_id

def reduceProductStockFromOrder(product):
    new_stock = product['product_stock'] - product['product_quantity']

    updateStock = update.update(
        table='product',
         colvalues={'productstock': new_stock},
                 where=[f'productid = {product["product_id"]}'])
    
    print("Reduced product ID: ", product['product_id'] , " stock to: ", new_stock, " from: ", product['product_stock'], " by: ", product['product_quantity'], " units.")
    return updateStock


def getOrderDetail(id: int):
    query = {"_id": ObjectId(id)}
    return list(mgdb.read('Orders', query))


#delete an order   
def deleteOrderSingle(orderId:int):
   mgdb.delete("Orders",{ "_id": orderId })


@app.route('/order', methods=["GET", "POST"])
def order():
    # Initialize an error message variable
    session.setdefault('error_message', [])
    if session.get('user_id') is None:
        session['error_message'] = "You must be logged in to place an order"
        return redirect(url_for('login'))

    if request.method == "POST":
        cart = getCart()
        products = getProducts(cart)
        ordertotal = getSubtotal(products)
        print("CART: ", cart)
        order_id = checkout(cart, ordertotal)
        print(order_id)
        order_detail = getOrderDetail(order_id)
        print(order_detail)

        return render_template('order.html', order_detail=order_detail, ordertotal=ordertotal, products=products)
    else:
        # If it's not a POST request, redirect to the homepage
        return redirect(url_for('homepage'))

@app.route('/cancel_order', methods=["GET", "POST"])
def selectCancelOrder():
     # Initialize an error message variable
    session.setdefault('error_message', [])
    if session.get('user_id') is None:
        session['error_message'] = "You must be logged in to view your cart"
        return redirect(url_for('login'))
    session.setdefault('status_message', [])
    if request.method == 'GET' and request.args.get('order_id'):
        order_id= request.args.get('order_id')
        order_status = list(mgdb.read('Orders',{ "_id": order_id }))[0]['status']
        if order_status == 'pending':
            setOrderStatus(order_id,'cancelled')
            session['status_message'] = "Order Cancelled."    
            return redirect(url_for('orders'))
        elif order_status == 'cancelled':
            session['error_message'] = "Order has already been cancelled."
            return redirect(url_for('orders'))
        else:
            session['error_message'] = "Order does not exist."
            return redirect(url_for('orders'))
    

@app.route('/ship_order', methods=["GET", "POST"])
def selectShipOrder():

    if 'user_id' in session:
        # Check if user is admin
        user = read.select(
            table='public.user',
            columns=['usertype'],
            where=[f'userid={session["user_id"]}'],
        )
        user_type = user[0][0]
        if user_type != 'admin':
            session['error_message'] = "You are not authorized to visit this page!"
            return redirect(url_for('homepage'))
     # Initialize an error message variable
    session.setdefault('error_message', [])
    if session.get('user_id') is None:
        session['error_message'] = "You must be logged in to view your cart"
        return redirect(url_for('login'))
    session.setdefault('status_message', [])
    if request.method == 'GET' and request.args.get('order_id'):
        order_id= request.args.get('order_id')
        order_status = list(mgdb.read('Orders',{ "_id": order_id }))[0]['status']
        if order_status == 'pending':
            setOrderStatus(order_id,'shipped')
            session['status_message'] = "Order Shipped."    
            return redirect(url_for('admin_orders'))
        elif order_status == 'cancelled':
            session['error_message'] = "Order has been cancelled."
            return redirect(url_for('admin_orders'))
        else:
            session['error_message'] = "Order does not exist."
            return redirect(url_for('admin_orders'))