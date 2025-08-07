# 🚨 Guía de Arreglos Rápidos

## 🔧 **CORRECCIONES APLICADAS - Reconstruir Contenedor**

### ❗ **IMPORTANTE: DEBES RECONSTRUIR COMPLETAMENTE**

```bash

docker-compose down

docker system prune -f

docker-compose build --no-cache

docker-compose up
```

## 🐛 **Errores Corregidos:**

### ✅ **1. Error de Zona Horaria (ZoneInfoNotFoundError)**
**Problema**: `No time zone found with key UTC`  
**Solución**: Instalado `tzdata` y configurado zona horaria Venezuela

### ✅ **2. Template JavaScript Error**  
**Problema**: Errores de sintaxis en test_chat.html  
**Solución**: Usado `json_script` filter para pasar datos a JavaScript

### ✅ **3. Middleware Complejo**  
**Problema**: Middleware personalizado causaba errores  
**Solución**: Simplificado a usar solo AuthMiddlewareStack estándar

### ✅ **4. Consumer Error Handling**  
**Problema**: Sin manejo robusto de errores  
**Solución**: Mejorado try-catch y validaciones

---

## 📋 **PASOS PARA VERIFICAR QUE FUNCIONA:**

### **1. Verificar Logs de Startup**
```bash
docker-compose logs web | grep -E "(✅|❌|Starting|Django setup)"
```

**Deberías ver**:
- ✅ Django setup successful
- ✅ Daphne started successfully (o Django runserver started)
- ✅ Apache server started

### **2. Verificar Servicios**
```bash
docker-compose exec web /app/healthcheck.sh

```

### **3. Probar Aplicación**
```bash
http://localhost:8000/login/

```

### **4. Probar Chat (SI LA APP FUNCIONA)**
```bash
http://localhost:8000/test-chat/test_room/

```

---

## 🚨 **SI AÚN NO FUNCIONA:**

### **Error 500 en cualquier página:**
```bash
docker-compose logs web | tail -50

docker-compose logs web | grep -i "error\|exception\|traceback"
```

### **Daphne no inicia:**
```bash
docker-compose exec web python3 manage.py check

docker-compose exec web python3 -c "from funATI.asgi import application; print('ASGI OK')"
```

### **Apache no proxy correctamente:**
```bash
curl http://localhost:8001/login/

docker-compose exec web apache2ctl status
```

---

## 🆘 **SOLUCIÓN DE EMERGENCIA:**

Si nada funciona, usar modo simple sin WebSockets:

### **1. Desactivar Channels temporalmente:**
```python
```

### **2. Usar solo WSGI:**
```bash
python3 manage.py runserver 0.0.0.0:8001 &
```

### **3. Verificar que funcione:**
```bash
docker-compose up --build
```

---

## 📞 **INFORMACIÓN DE DEBUG:**

### **Comandos útiles:**
```bash
docker-compose logs -f web

docker-compose exec web bash

docker-compose exec web python3 --version
docker-compose exec web python3 -c "import django; print(django.get_version())"

docker-compose exec web python3 manage.py dbshell

docker-compose exec web python3 manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.all())"
```

### **Archivos importantes a revisar:**
- `/app/funATI/funATI/settings.py` - Configuración Django
- `/app/funATI/funATI/asgi.py` - Configuración ASGI
- `/etc/apache2/sites-available/funati.conf` - Configuración Apache

---

**🎯 Con estas correcciones, el sistema debería funcionar. Si persisten problemas, es probable que sea un problema de la aplicación Django original, no del contenedor.** 