# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    patronymic = models.CharField(u'Отчество', max_length=250, blank=True, null=True)
    role_saler = models.BooleanField(u'Менеджер', default=False)
    role_admin = models.BooleanField(u'Администратор', default=False)
    role_driver = models.BooleanField(u'Водитель', default=False)
    role_lifter = models.BooleanField(u'Грузчик', default=False)
    role_accountant = models.BooleanField(u'Бухгалтер', default=False)

    class Meta:
        verbose_name = u'Персонал'
        verbose_name_plural = u'Персонал'
        ordering = ('last_name',)

    @property
    def fullname(self):
        return '{} {} {}'.format(self.last_name, self.first_name, self.patronymic)

    def __unicode__(self):
        return self.get_full_name()
