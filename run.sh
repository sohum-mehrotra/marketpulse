#!/bin/sh

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Initialize database (safe to re-run)
python3 - << 'EOF'
from src.db import init_db
print("Initializing database...")
init_db(rebuild=False)
print("Database ready.")
EOF

# Run the Flask app via gunicorn (production)
echo "Starting MarketPulse at port ${PORT:-10000}"
exec gunicorn -w 4 -b 0.0.0.0:${PORT:-10000} "src.app:create_app()"
