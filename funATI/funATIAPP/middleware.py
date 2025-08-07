from channels.auth import AuthMiddlewareStack
import logging
from django.utils import translation
from .models import UserSettings

logger = logging.getLogger(__name__)

def QueryAuthMiddlewareStack(inner):
    """
    Simplified middleware stack that just uses Django's standard auth
    """
    return AuthMiddlewareStack(inner)

class UserLanguageMiddleware:
    """
    Middleware para activar automáticamente el idioma del usuario
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                user_settings = UserSettings.get_user_settings(request.user)
                if user_settings.language:
                    translation.activate(user_settings.language)
                    request.LANGUAGE_CODE = user_settings.language
            except:
                # Si hay algún error, usar el idioma por defecto
                pass
        
        response = self.get_response(request)
        return response 