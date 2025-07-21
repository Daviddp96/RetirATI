FROM ubuntu:22.04

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y apache2 libapache2-mod-wsgi-py3 python3 python3-pip python3-dev python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Create virtual environment
RUN python3 -m venv env

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN /app/env/bin/pip install -r /app/requirements.txt

# Copy project files
COPY . /app/funATIAPP/

# Verify Django installation
RUN /app/env/bin/python3 -c "import django; print('Django version:', django.get_version())"

# Add ServerName to Apache configuration
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Copy Apache configuration
COPY apache-funati.conf /etc/apache2/sites-available/000-default.conf

# Enable mod_wsgi
RUN a2enmod wsgi

# Create necessary directories
RUN mkdir -p /app/funATIAPP/funATI/staticfiles && \
    mkdir -p /app/funATIAPP/funATI/media

# Change to Django project directory and run setup commands
WORKDIR /app/funATIAPP/funATI
RUN /app/env/bin/python manage.py migrate && \
    /app/env/bin/python manage.py collectstatic --noinput

# Set proper permissions
RUN chown -R www-data:www-data /app/funATIAPP/ && \
    chmod -R 755 /app/funATIAPP/

# Expose port
EXPOSE 80

# Start Apache in foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]