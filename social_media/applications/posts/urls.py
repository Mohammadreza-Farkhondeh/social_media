from django.urls import path
from . import views

app_name = 'posts'

# urlpatterns = [
#     path('', views.PostList.as_view(), name='post-list'), # GET all posts or POST a new post
#     path('<int:pk>/', views.PostDetail.as_view(), name='post-detail'), # GET, PUT/PATCH or DELETE a specific post
#     path('<int:pk>/comments/', views.CommentList.as_view(), name='comment-list'), # GET all comments for a specific post or POST a new comment
#     path('<int:pk>/comments/<int:ck>/', views.CommentDetail.as_view(), name='comment-detail'), # GET, PUT/PATCH or DELETE a specific comment
#     path('<int:pk>/likes/', views.LikeList.as_view(), name='like-list'), # GET all likes for a specific post or POST a new like
#     path('<int:pk>/likes/<int:lk>/', views.LikeDetail.as_view(), name='like-detail'), # GET or DELETE a specific like
# ]
urlpatterns= []