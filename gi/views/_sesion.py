from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from gi.carga_excel._add_error import add_user_id


class LoginView(View):
    def get(self, request):
        return render(request, "gi/views/sesion/index.html", {})

    def post(self, request):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        auth = authenticate(username=username, password=password)
        if auth and auth.is_active:
            login(request, auth)
            add_user_id(request.user.id)
            
            return redirect("gi:index")
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Credenciales inválidas. Por favor vuelva a intentarlo",
            )
            return redirect("gi:login")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("gi:login")
