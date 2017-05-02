# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import (authenticate, get_user_model)

User = get_user_model()

# CUSTOM LOGIN FORM
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(u'Такого пользователя не существует.')
            if not user.check_password(password):
                raise forms.ValidationError(u'Неправильный пароль.')
            if not user.is_active:
                raise forms.ValidationError(u'Данный пользователь заблокирован.')
        return super(UserLoginForm, self).clean(*args, **kwargs)
