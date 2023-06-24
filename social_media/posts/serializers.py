from rest_framework import serializers
from .models import Post, PostContent, Tag, Like, Recommendation


# A serializer class for the Tag model
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug')


# A serializer class for the PostContent model
class PostContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostContent
        fields = ('user', 'file',)


# A serializer class for the Post model
class PostSerializer(serializers.ModelSerializer):
    # Nested serializers for the user, tags and postcontent fields
    user = serializers.ReadOnlyField(source='user.email')
    tags = TagSerializer(many=True, read_only=True)
    postcontent = PostContentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('user', 'id', 'tags', 'content', 'posted', 'caption', 'postcontent')


class RecommendationPostSerializer(serializers.ModelSerializer):
    # Nested serializers for the user, tags and postcontent fields
    # post = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Recommendation
        fields = ('post',)


# A serializer class for the Like model
class LikeSerializer(serializers.ModelSerializer):
    # Nested serializer for the user and post fields
    user = serializers.ReadOnlyField(source='user.email')
    post = PostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'post',)
