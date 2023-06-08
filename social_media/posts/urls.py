from django.urls import path, include
from . import views

app_name = 'posts'

urlpatterns = [
    path('home', views.PostList.as_view(), name='post-list'),  # GET all posts or POST a new post
    path('explore/', views.exploreList.as_view(), name='explore-list'),  # GET all posts that recommended to user
    path('<int:pk>/', views.PostDetail.as_view(), name='post-detail'),  # GET, PUT/PATCH or DELETE a specific post
    path('<int:pk>/likes/', views.LikeList.as_view(), name='like-list'),  # GET all likes for a specific post or POST a new like
    path('<int:pk>/likes/<int:lk>/', views.LikeDetail.as_view(), name='like-detail'),  # GET or DELETE a specific like
    path('<int:pk>/comments', include('comments.urls')),
]
