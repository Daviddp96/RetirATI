FROM python:3.12.4

# Instalar Apache, mod_wsgi y dependencias necesarias
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    apache2-dev \
    lsb-release \
    && apt-get clean

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt y instalar las dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el contenido del repositorio al contenedor
COPY /funATI .

# Configurar Django para producción
ENV DJANGO_SETTINGS_MODULE=funATI.settings

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Configurar ALLOWED_HOSTS y STATIC_ROOT en settings.py
RUN sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['*']/" /app/funATI/settings.py
RUN echo "\nSTATIC_ROOT = '/app/staticfiles/'" >> /app/funATI/settings.py

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Aplicar migraciones de base de datos
RUN python manage.py migrate

# Cambiar la configuración de Apache para que escuche en el puerto 8080
RUN echo "Listen 8080" >> /etc/apache2/ports.conf

# Deshabilitar el sitio por defecto de Apache
RUN a2dissite 000-default

# Crear configuración personalizada para Django
RUN echo "<VirtualHost *:8080>\n\
    DocumentRoot /app\n\
    \n\
    WSGIScriptAlias / /app/funATI/wsgi.py\n\
    WSGIDaemonProcess django python-path=/app python-home=/usr/local\n\
    WSGIProcessGroup django\n\
    WSGIPassAuthorization On\n\
    \n\
    <Directory /app/funATI>\n\
        <Files wsgi.py>\n\
            Require all granted\n\
        </Files>\n\
    </Directory>\n\
    \n\
    # Servir archivos estáticos\n\
    Alias /static/ /app/staticfiles/\n\
    <Directory /app/staticfiles>\n\
        Require all granted\n\
    </Directory>\n\
    \n\
    # Servir archivos media (si los hay)\n\
    Alias /media/ /app/media/\n\
    <Directory /app/media>\n\
        Require all granted\n\
    </Directory>\n\
    \n\
    ErrorLog \${APACHE_LOG_DIR}/django_error.log\n\
    CustomLog \${APACHE_LOG_DIR}/django_access.log combined\n\
</VirtualHost>" > /etc/apache2/sites-available/django.conf

# Habilitar el sitio de Django
RUN a2ensite django

# Habilitar mod_wsgi en Apache
RUN a2enmod wsgi

# Cambiar permisos para que Apache pueda acceder a los archivos
RUN chown -R www-data:www-data /app
RUN chmod -R 755 /app

# Exponer el puerto 8080 para acceder a Apache
EXPOSE 8080

# Comando para iniciar Apache con mod_wsgi
CMD ["apache2ctl", "-D", "FOREGROUND"]