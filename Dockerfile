FROM ubuntu:22.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=funATI.settings
ENV PYTHONPATH=/app/funATI

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    apache2 \
    apache2-dev \
    libapache2-mod-wsgi-py3 \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    redis-server \
    curl \
    netcat-openbsd \
    tzdata \
    locales \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Caracas
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install mod_wsgi

COPY funATI/ /app/funATI/

RUN mkdir -p /app/funATI/staticfiles
RUN mkdir -p /app/funATI/media

RUN chown -R www-data:www-data /app/funATI/
RUN chmod -R 755 /app/funATI/

COPY apache-funati.conf /etc/apache2/sites-available/funati.conf

RUN a2enmod wsgi
RUN a2enmod rewrite
RUN a2enmod headers
RUN a2enmod mime
RUN a2enmod expires
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN a2enmod proxy_wstunnel
RUN a2dissite 000-default
RUN a2ensite funati

WORKDIR /app/funATI
RUN python3 manage.py collectstatic --noinput

COPY start.sh /app/start.sh
COPY healthcheck.sh /app/healthcheck.sh

# Convert line endings from Windows to Unix format (in case files were edited on Windows)
RUN dos2unix /app/start.sh /app/healthcheck.sh

# Make scripts executable
RUN chmod +x /app/start.sh /app/healthcheck.sh

EXPOSE 80

CMD ["/app/start.sh"] 