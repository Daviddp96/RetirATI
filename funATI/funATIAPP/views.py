def profile_detail_view(request, profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('funATIAPP:profile')
    publications = profile.publications.order_by('-created_at')
    return render(request, 'perfil-main.html', {'profile': profile, 'publications': publications})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .forms import PublicationForm, RegisterForm, LoginForm, RecoverPasswordForm
from .models import Publication, Profile, Comment
from django.http import JsonResponse
from random import sample
from django.db.models import Q

# Create your views here.

# Página de inicio (landing page)
def index(request):
    return render(request, 'index.html')

# Páginas de autenticación
def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return redirect('funATIAPP:muro')
            else:
                error = 'Credenciales incorrectas.'
        except User.DoesNotExist:
            error = 'No existe usuario con ese email.'
    return render(request, 'login.html', {'error': error})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Generar un username único basado en el email
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            return redirect('funATIAPP:login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def recover_password_view(request):
    if request.method == 'POST':
        form = RecoverPasswordForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='recoverpassword_email.html',
            )
            return render(request, 'recoverpassword.html', {'form': form, 'sent': True})
    else:
        form = RecoverPasswordForm()
    return render(request, 'recoverpassword.html', {'form': form})

# Páginas principales de la aplicación
def muro_view(request):
    if not request.user.is_authenticated:
        return redirect('funATIAPP:login')
    profile = request.user.profile
    # IDs de perfiles amigos y seguidos
    friends_ids = profile.friends.values_list('id', flat=True)
    following_ids = profile.following.values_list('id', flat=True)
    # Incluye tus propias publicaciones
    allowed_profiles = list(friends_ids) + list(following_ids) + [profile.id]
    publications = Publication.objects.select_related('profile__user').filter(profile_id__in=allowed_profiles).order_by('-created_at')
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.profile = profile
            publication.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('funATIAPP:muro')
    else:
        form = PublicationForm()
    return render(request, 'muro.html', {'form': form, 'publications': publications})

def notifications_view(request):
    return render(request, 'notifications.html')

def chats_view(request):
    return render(request, 'chats-main.html')

def friends_view(request):
    if not request.user.is_authenticated:
        return redirect('funATIAPP:login')
    profile = request.user.profile
    if request.method == 'POST':
        add_friend_id = request.POST.get('add_friend')
        follow_id = request.POST.get('follow')
        unfollow_id = request.POST.get('unfollow')
        remove_friend_id = request.POST.get('remove_friend')
        if add_friend_id:
            try:
                friend_profile = Profile.objects.get(id=add_friend_id)
                profile.friends.add(friend_profile)
                friend_profile.friends.add(profile)  # amistad mutua
            except Profile.DoesNotExist:
                pass
        if follow_id:
            try:
                follow_profile = Profile.objects.get(id=follow_id)
                profile.following.add(follow_profile)
            except Profile.DoesNotExist:
                pass
        if unfollow_id:
            try:
                unfollow_profile = Profile.objects.get(id=unfollow_id)
                profile.following.remove(unfollow_profile)
            except Profile.DoesNotExist:
                pass
        if remove_friend_id:
            try:
                friend_profile = Profile.objects.get(id=remove_friend_id)
                profile.friends.remove(friend_profile)
                friend_profile.friends.remove(profile)  # eliminar mutua
            except Profile.DoesNotExist:
                pass
        return redirect('funATIAPP:friends')
    all_profiles = Profile.objects.exclude(id=profile.id)
    friends = profile.friends.all()
    # Excluir amigos y el propio usuario de las recomendaciones
    exclude_ids = list(friends.values_list('id', flat=True)) + [profile.id]
    recommendations_qs = all_profiles.exclude(id__in=exclude_ids)
    recommendations = list(recommendations_qs)
    # Si hay menos de 15/4 usuarios, ajustar el sample
    if not friends:
        num_recommend = min(15, len(recommendations))
        recommendations = sample(recommendations, num_recommend) if num_recommend > 0 else []
        return render(request, 'friends.html', {
            'friends': [],
            'recommendations': recommendations
        })
    else:
        num_recommend = min(4, len(recommendations))
        recommendations = sample(recommendations, num_recommend) if num_recommend > 0 else []
        return render(request, 'friends.html', {
            'friends': friends,
            'recommendations': recommendations
        })

def settings_view(request):
    return render(request, 'settings.html')

def edit_profile_view(request):
    return render(request, 'edit-perfil.html')

def publication_view(request):
    return render(request, 'publication.html')

def profile_view(request):
    profile = request.user.profile
    publications = profile.publications.order_by('-created_at')
    return render(request, 'perfil-main.html', {'profile': profile, 'publications': publications})

def followers_view(request):
    # Permite ver los seguidores de cualquier perfil
    profile_id = request.GET.get('profile_id') or request.resolver_match.kwargs.get('profile_id')
    if profile_id:
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            profile = request.user.profile
    else:
        profile = request.user.profile
    followers = profile.followers.all()
    return render(request, 'followers.html', {'profile': profile, 'followers': followers})

def follows_view(request):
    # Permite ver los seguidos de cualquier perfil y dejar de seguir
    profile_id = request.GET.get('profile_id') or request.resolver_match.kwargs.get('profile_id')
    if profile_id:
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            profile = request.user.profile
    else:
        profile = request.user.profile

    if request.method == 'POST' and request.user.is_authenticated:
        unfollow_id = request.POST.get('unfollow')
        user_profile = request.user.profile
        if unfollow_id:
            try:
                to_unfollow = Profile.objects.get(id=unfollow_id)
                user_profile.following.remove(to_unfollow)
            except Profile.DoesNotExist:
                pass
        return redirect(request.path_info)

    following = profile.following.all()
    return render(request, 'follows.html', {'profile': profile, 'following': following})

# Componentes auxiliares
def menu_main_view(request):
    return render(request, 'menu-main.html')

def container_view(request):
    if not request.user.is_authenticated:
        return render(request, 'container.html', {'publications': []})
    profile = request.user.profile
    friends_ids = profile.friends.values_list('id', flat=True)
    following_ids = profile.following.values_list('id', flat=True)
    allowed_profiles = list(friends_ids) + list(following_ids) + [profile.id]
    publications = Publication.objects.select_related('profile__user').filter(profile_id__in=allowed_profiles).order_by('-created_at')
    return render(request, 'container.html', {'publications': publications})

def publication_detail_view(request, id):
    publication = Publication.objects.select_related('profile__user').get(id=id)
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        parent_id = request.POST.get('parent')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        if content:
            Comment.objects.create(
                publication=publication,
                user=request.user,
                content=content,
                parent=parent
            )
            return redirect('funATIAPP:publication_detail', id=id)
    comments = publication.comments.select_related('user').order_by('created_at')
    return render(request, 'publication.html', {
        'publication': publication,
        'comments': comments
    })
