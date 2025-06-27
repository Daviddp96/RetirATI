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

# Crear el proyecto Django (si no existe)
RUN django-admin startproject retirati .

# Copiar el contenido del repositorio al contenedor
COPY . .

# Cambiar la configuración de Apache para que escuche en el puerto 8080
RUN echo "Listen 8080" >> /etc/apache2/ports.conf

# Configurar el archivo de configuración de Apache para servir Django en el puerto 8080
RUN echo "<VirtualHost *:8080>\n\
    WSGIScriptAlias / /app/retirati/wsgi.py\n\
    <Directory /app/retirati>\n\
        <Files wsgi.py>\n\
            Require all granted\n\
        </Files>\n\
    </Directory>\n\
    ErrorLog ${APACHE_LOG_DIR}/error.log\n\
    CustomLog ${APACHE_LOG_DIR}/access.log combined\n\
</VirtualHost>" > /etc/apache2/sites-available/000-default.conf

# Habilitar mod_wsgi en Apache
RUN a2enmod wsgi

# Exponer el puerto 8080 para acceder a Apache
EXPOSE 8080

# Comando para iniciar Apache con mod_wsgi
CMD ["apache2ctl", "-D", "FOREGROUND"]