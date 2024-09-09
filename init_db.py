from models import Product, Vendor, InventoryTransaction

def init_db(db):
    with db.app.app_context():
        print("Creating database and tables...")
        db.create_all()
        print("Database and tables created.")