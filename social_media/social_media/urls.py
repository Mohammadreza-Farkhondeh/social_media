from django.contrib import admin
from django.urls import path, include


v1_patterns = [
    path('posts/', include('posts.urls')),
    path('users/', include('users.urls')),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(v1_patterns))
]


