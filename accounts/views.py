from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

# Create your views here.


def authenticate_view(request):
    if request.method == 'POST':
        data = request.POST.copy()
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'code': 'ok', 'message': _('登录成功')}, safe=False)
        else:
            return JsonResponse({'code': 'error', 'message': _('用户名或密码错误，登录失败')}, safe=False)


def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'code': 'ok', 'message': _('注册成功')}, safe=False)
        else:
            return JsonResponse({'code': 'error', 'message': _('注册失败')}, safe=False)


def reset_password_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        pass


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        user = request.user
        if user.id is None:
            return JsonResponse({'code': 'ok', 'message': _('注销成功')}, safe=False)
        else:
            return JsonResponse({'code': 'error', 'message': _('系统错误，请稍后再试')}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('系统错误，请稍后再试')}, safe=False)
