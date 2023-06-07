from django.contrib import admin
from django.urls import path, include


v1_patterns = [
    path('posts/', include('applications.posts.urls')),
    path('users/', include('applications.authy.urls')),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(v1_patterns))
]


