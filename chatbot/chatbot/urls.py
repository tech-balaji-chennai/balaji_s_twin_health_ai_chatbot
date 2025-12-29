# chatbot/chatbot/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Optional: Keep the admin interface for managing models
    path('admin/', admin.site.urls),

    # CRITICAL FIX: The include() function automatically adds a trailing slash
    # to the paths it generates. By removing the trailing slash from the path()
    # argument itself, we make the router correctly handle the boundary.
    # However, the standard fix is to ensure the path ends with a slash so the include
    # takes over cleanly.

    # The standard, correct way to include app URLs:
    path('api/', include('chat.urls')),
]
