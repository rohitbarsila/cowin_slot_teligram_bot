from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import WebHook

urlpatterns = [
    path('webhooks/', csrf_exempt(WebHook.as_view())),
]
