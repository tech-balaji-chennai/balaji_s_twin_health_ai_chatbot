# chat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # The main API endpoint: /api/classify/
    path('classify/', views.chat_classification_api, name='classify_chat'),
]
