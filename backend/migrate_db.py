import os
from app import app, db

def migrate_database():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

if __name__ == '__main__':
    migrate_database()
