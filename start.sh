
redis-server --daemonize yes

sleep 2

cd /app/funATI

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

echo "Starting Daphne server..."
cd /app/funATI

export DJANGO_SETTINGS_MODULE=funATI.settings
export PYTHONPATH=/app/funATI:$PYTHONPATH

echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

echo "Testing Django setup..."
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funATI.settings')
django.setup()
print('Django setup successful')
print('Available apps:', [app.name for app in django.apps.apps.get_app_configs()])
" || {
    echo "Django setup failed, trying alternative..."
    export DJANGO_SETTINGS_MODULE=funATI.settings
}

echo "Testing Channels configuration..."
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funATI.settings')
django.setup()
from django.conf import settings
print('ASGI_APPLICATION:', getattr(settings, 'ASGI_APPLICATION', 'Not configured'))
print('CHANNEL_LAYERS:', getattr(settings, 'CHANNEL_LAYERS', 'Not configured'))
" || echo "Channels test failed"

echo "Starting Daphne with command: daphne -b 0.0.0.0 -p 8001 -v 2 funATI.asgi:application"
daphne -b 0.0.0.0 -p 8001 -v 2 funATI.asgi:application &
DAPHNE_PID=$!

echo "Daphne PID: $DAPHNE_PID"

sleep 2

if ! kill -0 $DAPHNE_PID 2>/dev/null; then
    echo "❌ Daphne failed to start, trying alternative method..."
    
    echo "🔄 Starting with Django runserver..."
    python3 manage.py runserver 0.0.0.0:8001 --verbosity=2 &
    DAPHNE_PID=$!
    
    sleep 3
    if ! kill -0 $DAPHNE_PID 2>/dev/null; then
        echo "❌ Both Daphne and runserver failed!"
        echo "🔍 Checking Python and Django status..."
        python3 --version
        python3 -c "import django; print('Django version:', django.get_version())"
        python3 -c "import channels; print('Channels version:', channels.__version__)"
        exit 1
    else
        echo "✅ Django runserver started successfully"
    fi
else 
    echo "✅ Daphne started successfully"
fi

sleep 3

if kill -0 $DAPHNE_PID 2>/dev/null; then
    echo "Daphne started successfully on port 8001"
else
    echo "Failed to start Daphne"
    exit 1
fi

echo "Starting Apache server..."
apache2ctl -DFOREGROUND 