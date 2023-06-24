from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, LikeSerializer, RecommendationPostSerializer
from .models import Post, Like, Follow, Recommendation
from .utils import generate_recommendations


# A view class for the Post model
class PostList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        # get the users who the current user is following
        following = Follow.objects.filter(follower=user).values('following')
        # get the posts of those users
        posts = Post.objects.filter(user__in=following).order_by('-posted')
        return posts

    def perform_create(self, serializer):
        # Set the user field to the current user when creating a new post
        serializer.save(user=self.request.user)


# A view class for explore page including recommender system
class ExploreList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecommendationPostSerializer

    def get_queryset(self):
        user = self.request.user  # Get the current user from the request
        generate_recommendations(user)  # Call the function to generate recommendations for the user
        return Recommendation.objects.filter(user=user)  # Return the recommendations for the user


# A view class for post detail page
class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()


# A view class for the Like model
class LikeList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LikeSerializer

    def get_queryset(self):
        # Filter the likes by post id provided in the url parameter
        queryset = Like.objects.all()
        post_id = self.kwargs['pk']
        queryset = queryset.filter(post__id=post_id)
        return queryset

    def perform_create(self, serializer):
        # Set the user field to the current user and the post field to the post id provided in the url parameter when creating a new like
        post_id = self.kwargs['pk']
        post = Post.objects.get(id=post_id)
        serializer.save(user=self.request.user, post=post)


class LikeDetail(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LikeSerializer

    def get_object(self):
        # Get the like instance by post id and like id provided in the url parameters
        post_id = self.kwargs['pk']
        like_id = self.kwargs['lk']
        like = Like.objects.get(id=like_id, post__id=post_id)
        return like
