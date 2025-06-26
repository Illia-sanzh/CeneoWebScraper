from app import app
from flask import render_template, redirect, request, url_for, abort
from app.forms import ProductIdForm
from app.models import Product
import os
import json


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract')
def display_form():
    form = ProductIdForm()
    return render_template('extract.html', form=form)

@app.route('/extract', methods=['POST'])
def extract():
    form = ProductIdForm(request.form)
    if form.validate():
        product_id = form.product_id.data
        product = Product(product_id)
        product.extract_name()
        product.extract_opinions()
        product.calculate_stats()
        product.generate_charts()
        product.save_opinions()
        product.save_info()
        return redirect(url_for("product", product_id=product_id))
    else:
        return render_template('extract.html', form=form)


@app.route('/product/<product_id>')
def product(product_id):
    reviews = []
    file_path = f'./app/data/opinions/{product_id}.json'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    return render_template('product.html', reviews=reviews, product_id=product_id)

@app.route('/charts/<product_id>')
def charts(product_id):
    return render_template('charts.html', product_id=product_id)

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/about')
def about():
    return render_template('about.html')


