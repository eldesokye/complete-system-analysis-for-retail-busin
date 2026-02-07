#!/bin/bash
set -e

echo "Starting deployment script..."

# Run migrations (and seed data if SEED_DB=true)
echo "Running database migrations..."
python database/migrate.py

# Start the application
echo "Starting application..."
python main.py
