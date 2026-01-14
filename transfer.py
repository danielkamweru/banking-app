from app.database import engine, BASE
from app.models import User, Account, Transaction
import sqlalchemy

print(f"Connecting to: {engine.url}")

try:
    # This reaches into the database and forces a creation
    BASE.metadata.create_all(bind=engine)
    
    # Check if they actually exist now
    inspector = sqlalchemy.inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"Success! Tables found in DB: {tables}")
    
    if not tables:
        print("Wait... the command ran but the list is still empty.")
        
except Exception as e:
    print(f"Failed to connect or create: {e}")