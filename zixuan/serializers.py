import numpy as np
from analysis.models import StockHistoryDaily
from django.db import models
from investors.models import StockFollowing
from rest_framework import generics, routers, serializers, status, viewsets

from .models import CompanyDailyBasic, StockNameCodeMap
from django.utils.translation import gettext_lazy as _



