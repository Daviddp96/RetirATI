FROM python:3.12.4

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt y instala las dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN django-admin startproject retirati .

COPY . .

# Exponer el puerto de la aplicación
EXPOSE 8000

# Comando para iniciar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
