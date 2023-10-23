import math
from __main__ import app
from ricefield import create, read, update, delete
from flask import Flask, redirect, request, render_template, session, url_for
from PostGresControllerV2.PostGresControllerV2 import initialise_crud

def fetch_products_by_category(category_id, page):
    products_per_page = 12  # Number of products to display per page
    offset = (page - 1) * products_per_page
    products = read.select(
        table='product',
        joins = [{'type': 'INNER', 'table': 'subcategory', 'condition': 'product.subcategoryid = subcategory.subcategoryid'}],
        where= [f'categoryid = {category_id} ORDER BY productid ASC LIMIT {products_per_page} OFFSET {offset}'])
    return products

def get_category_name(category_id):
    category = read.select(table='category', where=[f'categoryid = {category_id}'])
    if category:
        return category[0][1].title()
    return "Category Not Found"

# TODO: For pagination
def get_total_products_in_category(category_id):
    products_per_page = 12
    products = read.select(
        columns=['COUNT(*)'],
        table='product',
        joins = [{'type': 'INNER', 'table': 'subcategory', 'condition': 'product.subcategoryid = subcategory.subcategoryid'}],
        where= [f'categoryid = {category_id}'])
    total_pages = math.ceil((products[0][0])/products_per_page)
    
    return total_pages

# e.g. http://127.0.0.1:5000/category?category=3&page=7
@app.route('/category', methods=["GET"])
def category():
    category_id = request.args.get('category', default=1, type=int)
    page = request.args.get('page', default=1, type=int)

    # TODO: Get total pages for pagination
    total_pages = get_total_products_in_category(category_id)

    # Get Category Name
    category_name = get_category_name(category_id)

    # Get Product Name
    products = fetch_products_by_category(category_id, page)

    # Calculate the starting and ending page numbers for pagination
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template('category.html', category_id=category_id, categoryName=category_name, products=products,
                           page=page, total_pages=total_pages, 
                           start_page=start_page, end_page=end_page)