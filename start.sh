#!/bin/bash
set -e

echo "🚀 Starting RetirATI application..."

# Start Redis server
echo "Starting Redis server..."
redis-server --daemonize yes

sleep 2

cd /app/funATI

# Verify Redis is running
echo "Verifying Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis not responding, but continuing..."
fi

python3 manage.py migrate

rm -rf /app/funATI/staticfiles/*
mkdir -p /app/funATI/staticfiles

python3 manage.py collectstatic --noinput --clear --verbosity=1

chown -R www-data:www-data /app/funATI/staticfiles/
chmod -R 755 /app/funATI/staticfiles/

echo "=== Static files structure ==="
ls -la /app/funATI/staticfiles/
echo "=== CSS files ==="
find /app/funATI/staticfiles/ -name "*.css" -type f
echo "=== JS files ==="
find /app/funATI/staticfiles/ -name "*.js" -type f
echo "=== Asset files ==="
find /app/funATI/staticfiles/ -name "*.png" -o -name "*.jpg" -o -name "*.svg" -type f

python3 manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

echo "🔧 Starting Django/Daphne server..."
cd /app/funATI

export DJANGO_SETTINGS_MODULE=funATI.settings
export PYTHONPATH=/app/funATI:$PYTHONPATH

echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

echo "🧪 Testing Django setup..."
python3 -c "
import os
import django
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funATI.settings')
    django.setup()
    print('✅ Django setup successful')
    print('Available apps:', [app.name for app in django.apps.apps.get_app_configs()])
except Exception as e:
    print('⚠️ Django setup error:', str(e))
    print('Continuing anyway...')
"

echo "🧪 Testing Channels configuration..."
python3 -c "
import os
import django
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funATI.settings')
    django.setup()
    from django.conf import settings
    print('✅ ASGI_APPLICATION:', getattr(settings, 'ASGI_APPLICATION', 'Not configured'))
    print('✅ CHANNEL_LAYERS:', getattr(settings, 'CHANNEL_LAYERS', 'Not configured'))
except Exception as e:
    print('⚠️ Channels test error:', str(e))
    print('Continuing anyway...')
"

echo "🚀 Starting Daphne server..."
echo "Command: daphne -b 0.0.0.0 -p 8001 -v 2 funATI.asgi:application"

# Try to start Daphne
daphne -b 0.0.0.0 -p 8001 -v 2 funATI.asgi:application &
DAPHNE_PID=$!

echo "Daphne PID: $DAPHNE_PID"
sleep 5

# Check if Daphne is still running
if kill -0 $DAPHNE_PID 2>/dev/null; then
    echo "✅ Daphne started successfully on port 8001"
else
    echo "❌ Daphne failed to start, trying Django runserver as fallback..."
    
    # Kill any remaining processes
    pkill -f "daphne" 2>/dev/null || true
    
    # Start Django runserver as fallback
    python3 manage.py runserver 0.0.0.0:8001 --verbosity=2 &
    DAPHNE_PID=$!
    
    sleep 5
    if kill -0 $DAPHNE_PID 2>/dev/null; then
        echo "✅ Django runserver started successfully as fallback"
    else
        echo "❌ Both Daphne and runserver failed!"
        echo "🔍 System diagnostics:"
        python3 --version
        python3 -c "import django; print('Django version:', django.get_version())" 2>/dev/null || echo "Django import failed"
        python3 -c "import channels; print('Channels version:', channels.__version__)" 2>/dev/null || echo "Channels import failed"
        echo "⚠️ Continuing with Apache only (static files will work)"
    fi
fi

echo "Starting Apache server..."
apache2ctl -DFOREGROUND