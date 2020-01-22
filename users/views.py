from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView

from .models import User


# Create your views here.
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
