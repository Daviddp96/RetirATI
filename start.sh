#!/bin/bash

# Script de inicio para configurar Django y Apache

# Activar el entorno virtual
source /app/env/bin/activate

# Ir al directorio del proyecto Django
cd /app/funATIAPP/funATI

# Configurar ALLOWED_HOSTS en settings.py
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['*']/" /app/funATIAPP/funATI/funATI/settings.py

# Agregar STATIC_ROOT si no existe
if ! grep -q "STATIC_ROOT" /app/funATIAPP/funATI/funATI/settings.py; then
    echo "STATIC_ROOT = '/app/funATIAPP/funATI/staticfiles/'" >> /app/funATIAPP/funATI/funATI/settings.py
fi

# Crear directorio para archivos estáticos
mkdir -p /app/funATIAPP/funATI/staticfiles
mkdir -p /app/funATIAPP/funATI/media

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Cambiar permisos para que Apache pueda acceder
chown -R www-data:www-data /app/funATIAPP/
chmod -R 755 /app/funATIAPP/

# Habilitar mod_wsgi
a2enmod wsgi

# Iniciar Apache en primer plano
apache2ctl -D FOREGROUND 