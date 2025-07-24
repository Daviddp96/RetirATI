#!/bin/bash

# Start Redis server in background
redis-server --daemonize yes

# Wait for Redis to start
sleep 2

# Navigate to Django project directory
cd /app/funATI

# Run Django migrations
python3 manage.py migrate

# Clear and collect static files
rm -rf /app/funATI/staticfiles/*
python3 manage.py collectstatic --noinput --clear

# Set proper permissions for static files
chown -R www-data:www-data /app/funATI/staticfiles/
chmod -R 755 /app/funATI/staticfiles/

# Debug: List static files structure
echo "=== Static files structure ==="
ls -la /app/funATI/staticfiles/
echo "=== CSS files ==="
find /app/funATI/staticfiles/ -name "*.css" -type f
echo "=== JS files ==="
find /app/funATI/staticfiles/ -name "*.js" -type f
echo "=== Asset files ==="
find /app/funATI/staticfiles/ -name "*.png" -o -name "*.jpg" -o -name "*.svg" -type f

# Create superuser if it doesn't exist (optional)
python3 manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Start Apache in foreground
apache2ctl -DFOREGROUND 