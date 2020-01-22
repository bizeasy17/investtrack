from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class User(AbstractUser):
    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_("姓名"), blank=True, max_length=255)
    picture = models.ImageField(
        _('个人头像'), upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(
        _('所在地区'), max_length=50, null=True, blank=True)
    job_title = models.CharField(
        _('头衔'), max_length=50, null=True, blank=True)
    personal_url = models.URLField(
        _('个人网址'), max_length=555, blank=True, null=True)
    facebook_account = models.URLField(
        _('Facebook账号'), max_length=255, blank=True, null=True)
    twitter_account = models.URLField(
        _('Twitter账号'), max_length=255, blank=True, null=True)
    github_account = models.URLField(
        _('GitHub账号'), max_length=255, blank=True, null=True)
    linkedin_account = models.URLField(
        _('LinkedIn账号'), max_length=255, blank=True, null=True)
    weibo_account = models.URLField(
        _('Weibo账号'), max_length=255, blank=True, null=True)
    weixin_account = models.URLField(
        _('Weixin账号'), max_length=255, blank=True, null=True)
    qq_account = models.URLField(
        _('QQ账号'), max_length=255, blank=True, null=True)
    short_bio = models.CharField(
        _('描述下你自己'), max_length=60, blank=True, null=True)
    bio = models.CharField(
        _('个人简介'), max_length=280, blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def get_profile_name(self):
        if self.name:
            return self.name

        return self.username
