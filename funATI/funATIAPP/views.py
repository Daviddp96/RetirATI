from django.shortcuts import render

# Create your views here.

# Página de inicio (landing page)
def index(request):
    return render(request, 'index.html')

# Páginas de autenticación
def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def recover_password_view(request):
    return render(request, 'recoverpassword.html')

# Páginas principales de la aplicación
def notifications_view(request):
    return render(request, 'notifications.html')

def chats_view(request):
    return render(request, 'chats-main.html')

def friends_view(request):
    return render(request, 'friends.html')

def settings_view(request):
    return render(request, 'settings.html')

def edit_profile_view(request):
    return render(request, 'edit-perfil.html')

def publication_view(request):
    return render(request, 'publication.html')

def profile_view(request):
    return render(request, 'perfil-main.html')

def followers_view(request):
    return render(request, 'followers.html')

def follows_view(request):
    return render(request, 'follows.html')

# Componentes auxiliares
def menu_main_view(request):
    return render(request, 'menu-main.html')

def container_view(request):
    return render(request, 'container.html')
