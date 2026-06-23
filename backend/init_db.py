"""
Initialize database with tables
Run this to create all tables
"""
from app.db.database import engine
from app.db.base import Base
from app.models import SMTPProfile, Campaign, Contact, EmailLog

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")
    
    # Print created tables
    print("\nCreated tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_db()
