from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PublicItem, UserLibrary

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            password=validated_data['password']
        )
        return user

class PublicItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicItem
        fields = '__all__'

class UserLibrarySerializer(serializers.ModelSerializer):
    item = PublicItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=PublicItem.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = UserLibrary
        fields = (
            'id', 
            'user', 
            'item', 
            'item_id', 
            'status', 
            'progress', 
            'rating', 
            'review', 
            'updated_at'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)