#!/bin/bash

# Configuration
# Auto-detect directory where the script is located
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$PROJECT_DIR/venv"

echo "🚀 Starting Deployment..."

# Navigate to project
cd $PROJECT_DIR

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input

# Restart Gunicorn (assuming you're using systemd)
echo "🔄 Restarting Gunicorn service..."
sudo systemctl restart gunicorn

echo "✅ Deployment Successful!"
