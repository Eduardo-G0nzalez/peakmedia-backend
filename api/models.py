from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class PublicItem(models.Model):
    ITEM_TYPES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('anime', 'Anime'),
        ('book', 'Book'),
        ('music', 'Music')
    ]
    
    api_id = models.CharField(max_length=100, unique=True) 
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    title = models.CharField(max_length=255)
    poster_url = models.URLField(max_length=1024, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    total_episodes = models.IntegerField(null=True, blank=True)
    total_chapters = models.IntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class UserLibrary(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('dropped', 'Dropped')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="library_items")
    item = models.ForeignKey(PublicItem, on_delete=models.CASCADE, related_name="user_entries")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned')
    progress = models.IntegerField(default=0)
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item') 
        verbose_name_plural = "User Libraries"

    def __str__(self):
        return f"{self.user.username} - {self.item.title} ({self.status})"