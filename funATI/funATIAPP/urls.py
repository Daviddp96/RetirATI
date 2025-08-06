from django.urls import path
from . import views

app_name = 'funATIAPP'

urlpatterns = [
    path('', views.index, name='index'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('recover-password/', views.recover_password_view, name='recover_password'),
    path('logout/', views.logout_view, name='logout'),
    
    path('app/', views.muro_view, name='app'),  
    path('muro/', views.muro_view, name='muro'),  
    path('notifications/', views.notifications_view, name='notifications'),
    path('chats/', views.chats_view, name='chats'),
    path('chat/<int:friend_id>/', views.chat_room_view, name='chat_room'),
    path('friends/', views.friends_view, name='friends'),
    path('settings/', views.settings_view, name='settings'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('change-language/', views.change_language_view, name='change_language'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('publication/', views.publication_view, name='publication'),
    path('publication/<int:id>/', views.publication_detail_view, name='publication_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:profile_id>/', views.profile_detail_view, name='profile_detail'),
    path('followers/', views.followers_view, name='followers'),
    path('followers/<int:profile_id>/', views.followers_view, name='followers_profile'),
    path('follows/', views.follows_view, name='follows'),
    path('follows/<int:profile_id>/', views.follows_view, name='follows_profile'),
    
    path('menu-main/', views.menu_main_view, name='menu_main'),
    path('container/', views.container_view, name='container'),
    
    path('api/messages/<int:friend_id>/', views.get_messages_api, name='get_messages_api'),
    path('api/search-friends/', views.search_friends_api, name='search_friends_api'),
    path('api/send-message/', views.send_message_api, name='send_message_api'),
    
    path('test-chat/<str:room_name>/', views.test_chat, name='test_chat'),
]