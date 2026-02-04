
import sys
import os
sys.path.append(os.getcwd())
import psycopg2
from config import settings

def apply_migration():
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT
        )
        cursor = conn.cursor()
        
        with open('database/migration_dwell.sql', 'r') as f:
            sql = f.read()
            
        cursor.execute(sql)
        conn.commit()
        print("Migration applied successfully!")
        
    except Exception as e:
        print(f"Error applying migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    apply_migration()
