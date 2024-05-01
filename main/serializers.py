from rest_framework import serializers

from . import models
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    auth = UserSerializer(read_only=True)

    class Meta:
        model = models.Authors
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Posts
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    class Meta:
        model = models.Comments
        fields = '__all__'
