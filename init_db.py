# init_db.py
import models, schemas, crud, database
from database import SessionLocal, engine

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)
print("Database tables created.")

db = SessionLocal()

# Check if admin user exists
db_admin = crud.get_user_by_username(db, username="admin")
if not db_admin:
    print("Admin user not found. Creating...")
    hashed_password = crud.get_password_hash("password")
    admin_user = models.User(username="admin", hashed_password=hashed_password, is_active=True)
    db.add(admin_user)
    db.commit()
    print("Admin user created with username 'admin' and password 'password'.")
else:
    print("Admin user already exists.")

db.close()