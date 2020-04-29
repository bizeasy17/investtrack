from datetime import datetime
from django.utils import timezone

def days_between(d1, d2):
  # d1 = datetime.strptime(d1, "%Y-%m-%d")
  # d2 = datetime.strptime(d2, "%Y-%m-%d")
  return abs((d2 - d1).days)

def days_to_now(d1):
  d2 = datetime.now(tz=timezone.utc)
  return abs((d2 - d1).days)