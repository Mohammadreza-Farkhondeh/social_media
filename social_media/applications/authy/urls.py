from . import views
from django.urls import path, include
from dj_rest_auth.views import LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'authy'

auth_patterns = [
    path('logout/', LogoutView.as_view(), name='logout'),  # POST token to logout and invalidate it
    path('auth/signup/', include('dj_rest_auth.registration.urls')),  # POST user details to register and get a token
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST username and password to login and get a token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # POST refresh token to create and get a new token
]

# users_patterns = [
#     path('', views.UserList.as_view(), name='user-list'), # GET all users or POST a new user
#     path('<int:pk>/', views.UserDetail.as_view(), name='user-detail'), # GET, PUT/PATCH or DELETE a specific user
#     path('<int:pk>/posts/', views.UserPostList.as_view(), name='user-post-list'), # GET all posts by a specific user
#     path('<int:pk>/followers/', views.FollowerList.as_view(), name='follower-list'), # GET all followers for a specific user or POST a new follower
#     path('<int:pk>/followers/<int:fk>/', views.FollowerDetail.as_view(), name='follower-detail'), # GET or DELETE a specific follower
# ]


urlpatterns = [
    # path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]