from django.contrib import admin
from .models import Choice
from .models import Post, Profile

admin.site.register(Post)
admin.site.register(Choice)
admin.site.register(Profile)