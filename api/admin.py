from django.contrib import admin
from .models import PublicItem, UserLibrary

@admin.register(PublicItem)
class PublicItemAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'item_type', 
        'api_id', 
        'release_date',
        'created_at'
    )
    search_fields = ('title', 'api_id', 'author')
    list_filter = ('item_type', 'release_date')
    ordering = ('-created_at',)

@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'item', 
        'status', 
        'rating',
        'progress',
        'updated_at'
    )
    search_fields = ('user__username', 'item__title') 
    list_filter = ('status', 'rating', 'item__item_type')
    ordering = ('-updated_at',)

    autocomplete_fields = ('user', 'item')