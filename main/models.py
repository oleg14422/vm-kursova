from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Authors(models.Model):
    auth = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16, default=None, null=True, blank=True)
    tg_id = models.CharField(max_length=20, default=None, null=True, blank=True)

    def __str__(self):
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.first_name}'


class Posts(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    short_description = models.CharField(max_length=127, default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.title} by {self.author}'


class Comments(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    content = models.TextField()
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"id: {self.id}, author: {self.author}, content: {self.content}"
