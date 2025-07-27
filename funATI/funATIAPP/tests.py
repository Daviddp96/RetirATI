# from django.test import TestCase

# Create your tests here.
# funATIAPP/tests.py
# funATIAPP/tests.py
# funATIAPP/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile
from django.utils import timezone

class UsuarioBasicoTest(TestCase):
    def test_creacion_usuario_basico(self):
        """
        Prueba básica que verifica que:
        1. Se puede crear un usuario
        2. Se crea automáticamente un perfil (vía señal)
        3. Podemos actualizar y verificar los campos del perfil
        """
        # 1. Crear usuario - esto activará la señal que crea el perfil automáticamente
        usuario = User.objects.create_user(
            username='usuarioprueba',
            email='prueba@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Usuario'
        )

        # 2. Obtener el perfil que fue creado automáticamente por la señal
        perfil = Profile.objects.get(user=usuario)
        
        # 3. Actualizar los campos del perfil
        perfil.biography = 'Biografía de prueba actualizada'
        perfil.birth_date = timezone.now().date()
        perfil.national_id = '12345678'
        perfil.favorite_color = 'Azul'
        perfil.save()

        # 4. Verificaciones
        # Verificar usuario
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(usuario.username, 'usuarioprueba')
        
        # Verificar perfil
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(perfil.user.username, 'usuarioprueba')
        self.assertEqual(perfil.biography, 'Biografía de prueba actualizada')
        self.assertEqual(perfil.national_id, '12345678')
        
        # Verificar el método __str__
        self.assertEqual(str(perfil), f"{usuario.username}'s Profile")