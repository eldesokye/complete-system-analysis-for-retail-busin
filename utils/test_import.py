import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting test...")
try:
    from database import get_db_manager
    print("Database manager imported successfully")
except Exception as e:
    print(f"Error: {e}")
print("Test finished")
