from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    favorite_color = models.CharField(max_length=50, blank=True, null=True)
    favorite_games = models.CharField(max_length=200, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    favorite_books = models.CharField(max_length=200, blank=True, null=True)
    favorite_music = models.CharField(max_length=200, blank=True, null=True)
    programming_languages = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Publication(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='publications')
    content = models.TextField()
    media = models.FileField(upload_to='media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publication by {self.profile.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
