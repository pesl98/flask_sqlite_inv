from app import app, db
from models import Product, Vendor, InventoryTransaction, OrderRequest, User

def recreate_tables():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Tables dropped and recreated.")

if __name__ == '__main__':
    recreate_tables()