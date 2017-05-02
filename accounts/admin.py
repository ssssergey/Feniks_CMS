# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import UserProfile
from django.contrib.auth.admin import UserAdmin


@admin.register(UserProfile)
class UserAdmin(UserAdmin):
    search_fields = ['last_name',]
    list_display = ('username', 'first_name', 'last_name', 'patronymic',)
    list_filter = ('role_saler', 'role_admin', 'role_driver', 'role_lifter')
    list_per_page = 20
    ordering = ['last_name']
    fieldsets = (
        (None, {'fields': ('password', 'username', 'last_name', 'first_name', 'patronymic')}),
        (u'Должность', {'fields': ('role_saler', 'role_admin', 'role_driver', 'role_lifter', 'role_accountant' )}),
        (u'Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (u'Даты', {'fields': ('last_login', 'date_joined')}),
    )