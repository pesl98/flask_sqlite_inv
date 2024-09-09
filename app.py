from flask import Flask, render_template, request, redirect, url_for, flash
from db import db, init_db
from models import Product, Vendor, InventoryTransaction, OrderRequest, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for flash messages

init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/products')
@login_required
def list_products():
    products = Product.query.all()
    return render_template('list_products.html', items=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        try:
            description = request.form['description']
            sku = request.form['sku']
            price = float(request.form['price'])
            warehouse_bins = request.form['warehouse_bins']
            reorder_point = int(request.form['reorder_point'])
            reorder_quantity = int(request.form['reorder_quantity'])
            images = request.form['images']
            specification = request.form['specification']
            vendor_id = int(request.form['vendor_id'])

            new_product = Product(
                description=description,
                sku=sku,
                price=price,
                warehouse_bins=warehouse_bins,
                reorder_point=reorder_point,
                reorder_quantity=reorder_quantity,
                images=images,
                specification=specification,
                vendor_id=vendor_id
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('list_products'))
        except ValueError as e:
            flash(str(e), 'error')

    vendors = Vendor.query.all()
    return render_template('add_product.html', vendors=vendors)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        try:
            product.description = request.form['description']
            product.sku = request.form['sku']
            product.price = float(request.form['price'])
            product.warehouse_bins = request.form['warehouse_bins']
            product.reorder_point = int(request.form['reorder_point'])
            product.reorder_quantity = int(request.form['reorder_quantity'])
            product.images = request.form['images']
            product.specification = request.form['specification']

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('list_products'))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('edit_product.html', product=product)

@app.route('/vendors')
@login_required
def list_vendors():
    vendors = Vendor.query.all()
    return render_template('list_vendors.html', items=vendors)

@app.route('/vendors/add', methods=['GET', 'POST'])
@login_required
def add_vendor():
    if request.method == 'POST':
        try:
            name = request.form['name']
            contact_person = request.form['contact_person']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']

            new_vendor = Vendor(
                name=name,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=address
            )
            db.session.add(new_vendor)
            db.session.commit()
            flash('Vendor added successfully!', 'success')
            return redirect(url_for('list_vendors'))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('add_vendor.html')

@app.route('/vendors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    if request.method == 'POST':
        try:
            vendor.name = request.form['name']
            vendor.contact_person = request.form['contact_person']
            vendor.email = request.form['email']
            vendor.phone = request.form['phone']
            vendor.address = request.form['address']

            db.session.commit()
            flash('Vendor updated successfully!', 'success')
            return redirect(url_for('list_vendors'))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('edit_vendor.html', vendor=vendor)

@app.route('/inventory_transactions')
@login_required
def inventory_transactions():
    transactions = InventoryTransaction.query.all()
    return render_template('inventory_transactions.html', items=transactions)

@app.route('/inventory_transactions/add', methods=['GET', 'POST'])
@login_required
def add_inventory_transaction():
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            transaction_type = request.form['transaction_type']
            quantity = int(request.form['quantity'])

            new_transaction = InventoryTransaction(
                product_id=product_id,
                transaction_type=transaction_type,
                quantity=quantity
            )
            db.session.add(new_transaction)
            db.session.commit()
            new_transaction.update_inventory_level()
            flash('Inventory transaction added successfully!', 'success')
            return redirect(url_for('inventory_transactions'))
        except ValueError as e:
            flash(str(e), 'error')

    products = Product.query.all()
    return render_template('add_inventory_transaction.html', products=products)

@app.route('/order_requests')
@login_required
def order_requests():
    order_requests = OrderRequest.query.all()
    return render_template('order_requests.html', items=order_requests)

@app.route('/order_requests/add', methods=['GET', 'POST'])
@login_required
def add_order_request():
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            vendor_id = request.form['vendor_id']
            reorder_quantity = int(request.form['reorder_quantity'])
            status = 'New'

            new_order_request = OrderRequest(
                product_id=product_id,
                vendor_id=vendor_id,
                reorder_quantity=reorder_quantity,
                status=status
            )
            db.session.add(new_order_request)
            db.session.commit()
            flash('Order request added successfully!', 'success')
            return redirect(url_for('order_requests'))
        except ValueError as e:
            flash(str(e), 'error')

    products = Product.query.all()
    vendors = Vendor.query.all()
    return render_template('add_order_request.html', products=products, vendors=vendors)

@app.route('/order_requests/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_order_request(id):
    order_request = OrderRequest.query.get_or_404(id)
    if request.method == 'POST':
        try:
            order_request.product_id = request.form['product_id']
            order_request.vendor_id = request.form['vendor_id']
            order_request.reorder_quantity = int(request.form['reorder_quantity'])
            order_request.status = request.form['status']

            db.session.commit()
            flash('Order request updated successfully!', 'success')
            return redirect(url_for('order_requests'))
        except ValueError as e:
            flash(str(e), 'error')

    products = Product.query.all()
    vendors = Vendor.query.all()
    return render_template('edit_order_request.html', order_request=order_request, products=products, vendors=vendors)

if __name__ == '__main__':
    app.run(debug=True)