# Setup Instructions for Windows

## Quick Setup (Recommended)

### Option 1: Using Your Existing Virtual Environment

Since you already have a `venv` folder, activate it first:

```powershell
# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python utils\init_db.py

# Generate demo data
python utils\demo_data.py

# Start the system
python main.py
```

### Option 2: Fresh Virtual Environment

If the above doesn't work, create a new virtual environment:

```powershell
# Remove old venv
Remove-Item -Recurse -Force venv

# Create new virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python utils\init_db.py

# Generate demo data
python utils\demo_data.py

# Start the system
python main.py
```

### Option 3: Without Virtual Environment (Not Recommended)

If you have Python installed globally:

```powershell
# Install dependencies globally
pip install -r requirements.txt

# Initialize database
python utils\init_db.py

# Generate demo data
python utils\demo_data.py

# Start the system
python main.py
```

## Troubleshooting

### "Python was not found"

This means Python isn't in your PATH. Options:

1. **Install Python**: Download from https://python.org (make sure to check "Add Python to PATH")
2. **Use py launcher**: Replace `python` with `py` in all commands
3. **Find Python**: Check if Python is installed:
   ```powershell
   where.exe python
   py --version
   ```

### "Execution policy error"

Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "ModuleNotFoundError"

Make sure you're in the virtual environment (you should see `(venv)` in your prompt):
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Database connection error

1. Make sure PostgreSQL is running
2. Check credentials in `.env` file
3. Verify database "supabase" exists

## Quick Test

After setup, test if everything works:

```powershell
# Check Python
python --version

# Check if packages are installed
pip list

# Test database connection
python -c "import psycopg2; print('PostgreSQL OK')"

# Test imports
python -c "from config import settings; print('Config OK')"
```

## Alternative: Use `py` launcher

If `python` command doesn't work, try using `py`:

```powershell
# Instead of: python utils\init_db.py
# Use: py utils\init_db.py

py utils\init_db.py
py utils\demo_data.py
py main.py
```

## Need Help?

If you're still having issues:

1. Check if Python is installed: `py --version` or `python --version`
2. Make sure you're in the project directory: `cd "d:\365 projects\new project"`
3. Activate virtual environment: `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`

Then try the setup commands again!
