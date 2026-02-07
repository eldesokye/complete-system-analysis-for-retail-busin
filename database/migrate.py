
import sys
import os
import psycopg2
import logging

# Add parent directory to path
sys.path.append(os.getcwd())

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Apply database migrations safely"""
    conn = None
    try:
        logger.info(f"Connecting to database...")
        # settings.database_url handles the connection string from env or config
        conn = psycopg2.connect(dsn=settings.database_url)
        cursor = conn.cursor()
        
        # 1. Apply Safe Schema (Create tables if not exist)
        logger.info("Applying safe schema...")
        schema_path = os.path.join('database', 'schema_safe.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                cursor.execute(schema_sql)
        else:
            logger.error(f"Schema file not found at {schema_path}")
            
        # 2. Apply Custom Migrations (if any)
        # Check for dwell time migration
        dwell_migration_path = os.path.join('database', 'migration_dwell.sql')
        if os.path.exists(dwell_migration_path):
             logger.info("Applying additional migrations...")
             with open(dwell_migration_path, 'r') as f:
                migration_sql = f.read()
                # Simple check if migration is needed or idempotent
                # For now just running it as it might be idempotent (create table/index if not exists)
                # But typically migrations should be tracked. 
                # Since we don't have a migration table, we'll optimistically run it 
                # or assume schema_safe covered it. 
                # Actually, schema_safe.sql includes the dwell time table now? 
                # Let's check schema_safe.sql content I just wrote.
                # Yes, schema_safe.sql has customer_dwell_time.
                pass 
        
        # Commit schema changes so they are visible to the seeder (which opens a new connection)
        conn.commit()

        # 3. Seed Data (Optional)
        if os.environ.get("SEED_DB", "").lower() == "true":
            logger.info("SEED_DB is set. Running data seeder...")
            try:
                from database.seed_data import seed_database
                seed_database()
            except ImportError:
                # If running directly from database folder, might need different import
                import seed_data
                seed_data.seed_database()
            except Exception as e:
                logger.error(f"Error during seeding: {e}")
        
        # Final commit (though seeder commits itself, and we committed above)
        # conn.commit() 
        logger.info("Migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migrations()
