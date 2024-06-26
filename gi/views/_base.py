import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View


class AuthenticatedView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and request.user.is_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("gi:login")


class DataView(AuthenticatedView):
    data = None

    def dispatch(self, request, *args, **kwargs):
        if request.method != "GET":
            try:
                self.data = json.loads(request.body.decode("utf-8"))
            except json.decoder.JSONDecodeError:
                return JsonResponse({"message": "Invalid request"}, status=400)
        try:
            return super().dispatch(request, *args, **kwargs)
        except IntegrityError as e:
            return JsonResponse({"message": f"Incomplete data ({str(e)})"}, status=400)
