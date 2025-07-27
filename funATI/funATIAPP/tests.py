# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile
from django.utils import timezone

class UsuarioBasicoTest(TestCase):
    def test_creacion_usuario_basico(self):
        """
        Prueba unitaria que verifica que:
        1. Se puede crear un usuario
        2. Se crea automáticamente un perfil
        3. Podemos actualizar y verificar los campos del perfil
        """
        # Crear usuario
        usuario = User.objects.create_user(
            username='usuarioprueba',
            email='prueba@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Usuario'
        )

        # Obtener el perfil que fue creado automáticamente por la señal
        perfil = Profile.objects.get(user=usuario)
        
        # Actualizar los campos del perfil
        perfil.biography = 'Biografía de prueba actualizada'
        perfil.birth_date = timezone.now().date()
        perfil.national_id = '12345678'
        perfil.favorite_color = 'Azul'
        perfil.save()

        # Verificar usuario
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(usuario.username, 'usuarioprueba')
        
        # Verificar perfil
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(perfil.user.username, 'usuarioprueba')
        self.assertEqual(perfil.biography, 'Biografía de prueba actualizada')
        self.assertEqual(perfil.national_id, '12345678')
        self.assertEqual(str(perfil), f"{usuario.username}'s Profile")

    def test_sistema_amigos(self):
        """
        Prueba unitaria que verifica:
        1. Que un perfil puede agregar a otro como amigo
        2. Que la relación es simétrica (si A es amigo de B, entonces B es amigo de A)
        3. Que el contador de amigos se incrementa correctamente
        """
        # Crear dos usuarios con sus perfiles
        usuario1 = User.objects.create_user(
            username='usuario1',
            email='usuario1@example.com',
            password='testpass123'
        )
        usuario2 = User.objects.create_user(
            username='usuario2',
            email='usuario2@example.com',
            password='testpass123'
        )
        perfil1 = Profile.objects.get(user=usuario1)
        perfil2 = Profile.objects.get(user=usuario2)
        
        # Establecer relación de amistad
        perfil1.friends.add(perfil2)
        
        # Verificar que usuario1 tiene a usuario2 como amigo
        self.assertEqual(perfil1.friends.count(), 1)
        self.assertEqual(perfil1.friends.first(), perfil2)
        
        # Verificar que la relación es simétrica (usuario2 también tiene a usuario1 como amigo)
        self.assertEqual(perfil2.friends.count(), 1)
        self.assertEqual(perfil2.friends.first(), perfil1)
        
        # Verificar nombres para mayor claridad
        self.assertEqual(perfil1.friends.first().user.username, 'usuario2')
        self.assertEqual(perfil2.friends.first().user.username, 'usuario1')