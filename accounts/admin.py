# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import UserProfile
from django.contrib.auth.admin import UserAdmin


@admin.register(UserProfile)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'patronymic',)
    list_filter = ('last_name', 'first_name', 'patronymic', 'username',)
    list_per_page = 20
    ordering = ['last_name']