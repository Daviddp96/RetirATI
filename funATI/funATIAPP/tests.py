# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Profile, Publication
from django.urls import reverse
from django.utils import timezone
import tempfile
from PIL import Image

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

class PublicacionesIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)
        self.client.login(username='testuser', password='testpass123')

    def test_flujo_completo_publicacion(self):
        """
        Prueba de integración que verifica:
        1. El usuario puede acceder al muro (muro/)
        2. Puede crear una publicación
        3. La publicación aparece en su perfil
        4. La vista de detalle muestra correctamente la publicación
        """
        # Verificar acceso al muro principal
        response = self.client.get(reverse('funATIAPP:muro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Muro')
        
        # Obtener CSRF token
        csrf_token = self.client.cookies['csrftoken'].value
        
        # Crear una publicación
        response = self.client.post(reverse('funATIAPP:muro'), {
            'content': 'Mi primera publicación de prueba',
            'csrfmiddlewaretoken': csrf_token
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la publicación existe en la base de datos
        publication = Publication.objects.first()
        self.assertIsNotNone(publication)
        self.assertEqual(publication.content, 'Mi primera publicación de prueba')
        self.assertEqual(publication.profile, self.profile)
        
        # Verificar que la publicación aparece en el perfil
        response = self.client.get(reverse('funATIAPP:profile'))
        self.assertContains(response, 'Mi primera publicación de prueba')
        
        # Verificar vista de detalle de publicación
        response = self.client.get(reverse('funATIAPP:publication_detail', args=[publication.id]))
        self.assertContains(response, 'Mi primera publicación de prueba')
        self.assertContains(response, 'testuser') # Verificar que el nombre de usuario aparece en la publicación