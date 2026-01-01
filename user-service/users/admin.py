"""
Admin configuration for users app.

Educational Note: Django admin provides a ready-to-use admin interface.
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# User model is already registered by Django, but we can customize it
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
