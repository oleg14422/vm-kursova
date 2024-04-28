from django.contrib import admin
from .models import Authors, Posts, Comments
# Register your models here.

class PostsAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'author', 'title']

admin.site.register(Authors)
admin.site.register(Posts, PostsAdmin)
admin.site.register(Comments)
