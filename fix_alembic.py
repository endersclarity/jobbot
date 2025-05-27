#!/usr/bin/env python3
"""Fix alembic version table"""

from app.core.database import engine
import sqlalchemy as sa

def fix_alembic():
    print("⚠️  WARNING: This will clear the Alembic version table!")
    confirm = input("Are you sure you want to continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
        
    try:
        with engine.begin() as conn:  # Use begin() for automatic transaction
            inspector = sa.inspect(engine)
            if 'alembic_version' in inspector.get_table_names():
                conn.execute(sa.text("DELETE FROM alembic_version"))
                print("✅ Cleared alembic_version table")
            else:
                print("ℹ️  No alembic_version table found")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    fix_alembic()