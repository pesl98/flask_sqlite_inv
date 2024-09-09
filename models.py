from db import db
from sqlalchemy.orm import validates
import re
from flask_login import UserMixin

print("Defining User model...")
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
            raise ValueError("Username must be between 3 and 50 characters and can only contain letters, numbers, and underscores")
        return username

    @validates('password')
    def validate_password(self, key, password):
        if not password:
            raise ValueError("Password is required")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

    @validates('role')
    def validate_role(self, key, role):
        if role not in ['admin', 'user']:
            raise ValueError("Invalid role")
        return role

print("Defining Product model...")
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    warehouse_bins = db.Column(db.String(255), nullable=False)
    reorder_point = db.Column(db.Integer, nullable=False)
    reorder_quantity = db.Column(db.Integer, nullable=False)
    images = db.Column(db.String(255))
    specification = db.Column(db.String(255))
    inventory_level = db.Column(db.Integer, nullable=False, default=0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

    vendor = db.relationship('Vendor', backref='products')

    @validates('sku')
    def validate_sku(self, key, sku):
        if not sku:
            raise ValueError("SKU is required")
        if not re.match(r'^[A-Z0-9]{3,50}$', sku):
            raise ValueError("SKU must be in uppercase and between 3 and 50 characters")
        return sku

    @validates('price')
    def validate_price(self, key, price):
        if price <= 0:
            raise ValueError("Price must be a positive number")
        return price

    @validates('reorder_point')
    def validate_reorder_point(self, key, reorder_point):
        if reorder_point < 0:
            raise ValueError("Reorder point must be a non-negative integer")
        return reorder_point

    @validates('reorder_quantity')
    def validate_reorder_quantity(self, key, reorder_quantity):
        if reorder_quantity < 0:
            raise ValueError("Reorder quantity must be a non-negative integer")
        return reorder_quantity

print("Defining Vendor model...")
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
            raise ValueError("Invalid email format")
        return email

    @validates('phone')
    def validate_phone(self, key, phone):
        if not phone:
            raise ValueError("Phone is required")
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            raise ValueError("Invalid phone number format")
        return phone

print("Defining product_vendor table...")
product_vendor = db.Table('product_vendor',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('vendor_id', db.Integer, db.ForeignKey('vendor.id'), primary_key=True)
)

print("Defining InventoryTransaction model...")
class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    product = db.relationship('Product', backref='transactions')

    def update_inventory_level(self):
        product = Product.query.get(self.product_id)
        if self.transaction_type == 'issue':
            product.inventory_level -= self.quantity
        elif self.transaction_type == 'receive':
            product.inventory_level += self.quantity
        db.session.commit()

        if product.inventory_level < product.reorder_point:
            self.generate_order_request(product)

    def generate_order_request(self, product):
        # Check if there is already an open order request for the product
        existing_order_request = OrderRequest.query.filter_by(product_id=product.id, status='New').first()
        if not existing_order_request:
            # Create a new order request
            order_request = OrderRequest(
                product_id=product.id,
                vendor_id=product.vendor_id,
                reorder_quantity=product.reorder_quantity,
                status='New'
            )
            db.session.add(order_request)
            db.session.commit()
            print(f"Order request generated for product {product.sku}")

print("Defining OrderRequest model...")
class OrderRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    reorder_quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='New')

    product = db.relationship('Product', backref='order_requests')
    vendor = db.relationship('Vendor', backref='order_requests')

    @validates('reorder_quantity')
    def validate_reorder_quantity(self, key, reorder_quantity):
        if reorder_quantity <= 0:
            raise ValueError("Reorder quantity must be a positive integer")
        return reorder_quantity

    @validates('status')
    def validate_status(self, key, status):
        if status not in ['New', 'Ordered', 'Closed/Received']:
            raise ValueError("Invalid status")
        return status