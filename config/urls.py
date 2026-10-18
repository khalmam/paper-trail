from django.http import JsonResponse
from django.urls import path

from api.endpoints import api


def health(_request):
    return JsonResponse({"ok": True})


urlpatterns = [path("health", health), path("api/", api.urls)]
