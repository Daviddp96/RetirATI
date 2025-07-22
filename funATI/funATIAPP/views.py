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
from .forms import PublicationForm, RegisterForm, LoginForm, RecoverPasswordForm, ProfileEditForm
from .models import Publication, Profile, Comment, Message, Notification
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
    if not request.user.is_authenticated:
        return redirect('funATIAPP:login')
    
    # Get all notifications for the current user
    notifications = request.user.notifications.all()[:20]  # Limit to 20 most recent
    
    # Mark notifications as read when viewed
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'notifications.html', {'notifications': notifications})

def chats_view(request):
    if not request.user.is_authenticated:
        return redirect('funATIAPP:login')
    
    profile = request.user.profile
    friends = profile.friends.all()
    
    # Get search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        friends = friends.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Add recent messages for each friend
    friends_with_messages = []
    for friend in friends:
        # Get last message between current user and this friend
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=friend.user) |
            Q(sender=friend.user, receiver=request.user)
        ).first()
        
        friends_with_messages.append({
            'friend': friend,
            'last_message': last_message
        })
    
    return render(request, 'chats-main.html', {
        'friends_with_messages': friends_with_messages,
        'search_query': search_query,
    })

def chat_room_view(request, friend_id):
    """View for specific chat room with a friend"""
    if not request.user.is_authenticated:
        return redirect('funATIAPP:login')
    
    try:
        friend_profile = Profile.objects.get(id=friend_id)
        # Check if they are friends
        if friend_profile not in request.user.profile.friends.all():
            return redirect('funATIAPP:chats')
    except Profile.DoesNotExist:
        return redirect('funATIAPP:chats')
    
    # Get chat messages between the two users
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=friend_profile.user) |
        Q(sender=friend_profile.user, receiver=request.user)
    ).order_by('timestamp')[:50]  # Last 50 messages
    
    # Mark messages from friend as read
    Message.objects.filter(
        sender=friend_profile.user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Generate room name for WebSocket (consistent naming)
    room_name = f"{min(request.user.id, friend_profile.user.id)}_{max(request.user.id, friend_profile.user.id)}"
    
    return render(request, 'chat-room.html', {
        'friend': friend_profile,
        'messages': messages,
        'room_name': room_name,
    })

def get_messages_api(request, friend_id):
    """API endpoint to get messages with a specific friend"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        friend_profile = Profile.objects.get(id=friend_id)
        friend_user = friend_profile.user
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Friend not found'}, status=404)
    
    # Get messages
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=friend_user) |
        Q(sender=friend_user, receiver=request.user)
    ).order_by('timestamp')[:50]
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'media_url': msg.media.url if msg.media else None,
        'sender_id': msg.sender.id,
        'sender_username': msg.sender.username,
        'timestamp': msg.timestamp.isoformat(),
        'is_sent': msg.sender == request.user,
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})

def search_friends_api(request):
    """API endpoint to search friends"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    search_query = request.GET.get('q', '')
    profile = request.user.profile
    
    if not search_query:
        # If no search query, return all friends with their last messages
        friends = profile.friends.all()
        friends_data = []
        for friend in friends:
            # Get last message between current user and this friend
            last_message = Message.objects.filter(
                Q(sender=request.user, receiver=friend.user) |
                Q(sender=friend.user, receiver=request.user)
            ).first()
            
            friends_data.append({
                'id': friend.id,
                'username': friend.user.username,
                'first_name': friend.user.first_name,
                'last_name': friend.user.last_name,
                'avatar_url': friend.avatar.url if friend.avatar else None,
                'last_message': {
                    'content': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else ''),
                    'timestamp': last_message.timestamp.strftime('%b %d') if last_message else '',
                    'is_unread': last_message and last_message.sender != request.user and not last_message.is_read if last_message else False
                } if last_message else None
            })
    else:
        # Filter friends by search query
        friends = profile.friends.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
        
        friends_data = [{
            'id': friend.id,
            'username': friend.user.username,
            'first_name': friend.user.first_name,
            'last_name': friend.user.last_name,
            'avatar_url': friend.avatar.url if friend.avatar else None,
        } for friend in friends]
    
    return JsonResponse({'friends': friends_data})

def send_message_api(request):
    """API endpoint to send a message with optional media"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content', '')
        media_file = request.FILES.get('media')
        
        if not receiver_id:
            return JsonResponse({'error': 'Receiver ID is required'}, status=400)
            
        if not content and not media_file:
            return JsonResponse({'error': 'Message content or media is required'}, status=400)
        
        try:
            receiver_profile = Profile.objects.get(id=receiver_id)
            receiver_user = receiver_profile.user
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Receiver not found'}, status=404)
        
        # Check if they are friends
        if receiver_profile not in request.user.profile.friends.all():
            return JsonResponse({'error': 'You can only send messages to friends'}, status=403)
        
        # Create the message
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver_user,
            content=content,
            media=media_file if media_file else None
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'media_url': message.media.url if message.media else None,
                'sender_id': message.sender.id,
                'sender_username': message.sender.username,
                'timestamp': message.timestamp.isoformat(),
                'is_sent': True,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('funATIAPP:profile')
    else:
        form = ProfileEditForm(instance=request.user.profile, user=request.user)
    
    return render(request, 'edit-perfil.html', {
        'form': form,
        'profile': request.user.profile
    })

def publication_view(request):
    return render(request, 'publication.html')

def profile_view(request):
    profile = request.user.profile
    publications = profile.publications.order_by('-created_at')
    return render(request, 'perfil-main.html', {'profile': profile, 'publications': publications})

def followers_view(request, profile_id=None):
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

def follows_view(request, profile_id=None):
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
    context = {}
    if request.user.is_authenticated:
        context['user'] = request.user
        context['profile'] = request.user.profile
    return render(request, 'menu-main.html', context)

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
