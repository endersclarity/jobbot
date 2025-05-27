#!/usr/bin/env python3
"""Debug database connection and table existence"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

def check_database():
    try:
        with engine.connect() as conn:
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print("📋 Available tables:")
            for table in tables:
                print(f"  - {table}")
            
            # Check specific analytics tables
            analytics_tables = ['companies', 'lead_scores', 'roi_metrics', 'predictive_models', 'analytics_business_metrics']
            print("\n🔍 Analytics tables status:")
            for table in analytics_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table}")
            
            return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    check_database()