from __main__ import app
from flask import Flask, redirect, request, render_template, session, url_for
from congoDB import read, create, update, delete
from controller.mongodbController import MongoDBController
from app_pages.cart import getProducts, getSubtotal
from app_pages.order import getOrderDetail

mgdb = MongoDBController()

def getSingleOrder(order_id):
    orders=mgdb.read("Orders",{ "_id": order_id })
    orderList=list(orders)
    return orderList


@app.route('/single_order', methods=["GET", "POST"])
def singleOrder():
    admin = False
    # Initialize an error message variable
    session.setdefault('error_message', [])
    if session.get('user_id') is None:
        session['error_message'] = "You must be logged in to view your cart"
        return redirect(url_for('login'))
    
    if 'user_id' in session:
        # Check if user is admin
        user = read.select(
            table='public.user',
            columns=['usertype'],
            where=[f'userid={session["user_id"]}'],
        )
        user_type = user[0][0]
        if user_type == 'admin':
            admin = True
    

    if request.method == 'GET':
        order_id=request.args.get('order_id')
        print(order_id)
        orderList= getSingleOrder(order_id)
        order_detail = getOrderDetail(order_id)
        products = getProducts(orderList[0])
        ordertotal = getSubtotal(products)

    return render_template('single_order.html', products=products, ordertotal=ordertotal ,order_detail=order_detail,admin = admin)