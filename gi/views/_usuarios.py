from django.contrib.auth.models import User
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from gi.models import Usuario, Ciudad
from gi.utils import get_grupos_gestion_usuario, get_users
from ._base import DataView, AuthenticatedView


class AdministracionUsuariosView(AuthenticatedView):
    def get(self, request):
        data, pages, total = get_users(request)
        qs = get_grupos_gestion_usuario(request.user)
        grupos_gestion = list(
            qs.annotate(slug=F("id"), value=F("id"), label=F("nombre")).values(
                "slug", "label", "value"
            )
        )
        return render(
            request,
            "gi/views/usuarios/administracion-usuarios.html",
            {
                "title": "Administración de usuarios",
                "aside": "",
                "data": data,
                "pages": pages,
                "total": total,
                "grupos_gestion": grupos_gestion,
                "cities": list(Ciudad.objects.values(label=F("nombre"), value=F("id"))),
            },
        )


class UpdateAdminView(DataView):
    def post(self, request):
        try:
            fk_user = User(username=self.data.get("name"), email=self.data.get("email"))

            fk_user.save()
            user = Usuario(fk_user_django=fk_user)
            user.todos_grupos_gestion = self.data.get("todos_grupos_gestion", False)
            user.save()

            if not user.todos_grupos_gestion:
                ids = [i.get("slug") for i in self.data.get("grupos_gestion")]
                grupos_gestion = get_grupos_gestion_usuario(request.user).filter(
                    id__in=ids
                )
                for i in grupos_gestion:
                    user.grupos_gestion.add(i)
                user.save()
            return JsonResponse({"user": user.to_dict})
        except Usuario.DoesNotExist:
            return JsonResponse({"message": "El usuario no existe"}, status=404)

    def delete(self, request):
        try:
            Usuario.objects.filter(id__in=self.data.get("users", [])).delete()
            return JsonResponse({})
        except ValueError:
            return JsonResponse({}, status=404)

    def put(self, request):
        try:
            user = Usuario.objects.get(id=self.data.get("id"))
            user.fk_user_django.username = self.data.get("name")
            user.fk_user_django.email = self.data.get("email")
            user.fk_user_django.save()
            user.todos_grupos_gestion = self.data.get("todos_grupos_gestion", False)
            if user.todos_grupos_gestion:
                user.grupos_gestion.clear()
            else:
                ids = [i.get("slug") for i in self.data.get("grupos_gestion")]
                grupos_gestion = get_grupos_gestion_usuario(request.user).filter(
                    id__in=ids
                )
                user.grupos_gestion.clear()
                for i in grupos_gestion:
                    user.grupos_gestion.add(i)

            user.save()

            user.fk_user_django.groups.clear()
            return JsonResponse({"user": user.to_dict})
        except Usuario.DoesNotExist:
            return JsonResponse({"message": "El usuario no existe"}, status=404)


class AdministracionUsuariosApiView(DataView):
    def get(self, request):
        data, pages, total = get_users(request)
        return JsonResponse({"data": data, "pages": pages, "total": total})
