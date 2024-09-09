from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def add_admin_user():
    with app.app_context():
        # Check if the admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create a new admin user
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin_password', method='pbkdf2:sha256'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user added successfully!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    add_admin_user()