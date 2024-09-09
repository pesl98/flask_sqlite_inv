from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        print("Creating database and tables...")
        db.create_all()
        print("Database and tables created.")