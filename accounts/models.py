# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, AbstractUser


class UserProfile(AbstractUser):
    patronymic = models.CharField(u'Отчество', max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = u'Менеджер'
        verbose_name_plural = u'Менеджеры'

    @property
    def fullname(self):
        return '{} {} {}'.format(self.last_name, self.first_name, self.patronymic)

    def __unicode__(self):
        return self.fullname
