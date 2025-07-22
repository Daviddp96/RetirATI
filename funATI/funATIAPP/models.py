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
    friends = models.ManyToManyField('self', symmetrical=True, blank=True, related_name='friends_with')
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Publication(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='publications')
    content = models.TextField()
    media = models.FileField(upload_to='media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publication by {self.profile.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Comment(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    def __str__(self):
        return f"Comentario de {self.user.username} en {self.publication.id}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)  # Allow empty content for media-only messages
    media = models.FileField(upload_to='chat_media/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Mensaje de {self.sender.username} para {self.receiver.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('friend', 'Friend'),
        ('comment', 'Comment'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificación para {self.recipient.username} de {self.sender.username} - {self.get_notification_type_display()}"
