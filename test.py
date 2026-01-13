from app.database import SessionLocal, engine, BASE
from app.models import User

 

BASE.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    print(f"Connecting to database...")
    new_user = User(
        first_name="Tommy",
        last_name="Test",
        email="tommy@test.com",
        phone_number=12345678,
        hashed_pin=1234 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f" Success! User {new_user.first_name} created with ID {new_user.id}")
except Exception as e:
    print(f" Error: {e}")
finally:
    db.close()