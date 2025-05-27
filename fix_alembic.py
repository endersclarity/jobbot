#!/usr/bin/env python3
"""Fix alembic version table"""

from app.core.database import engine
import sqlalchemy as sa

def fix_alembic():
    with engine.connect() as conn:
        # Check if alembic_version exists
        inspector = sa.inspect(engine)
        if 'alembic_version' in inspector.get_table_names():
            # Clear the alembic_version table
            conn.execute(sa.text("DELETE FROM alembic_version"))
            conn.commit()
            print("Cleared alembic_version table")
        else:
            print("No alembic_version table found")

if __name__ == "__main__":
    fix_alembic()