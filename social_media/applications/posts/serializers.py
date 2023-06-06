from rest_framework import Serializers
from .models import Post



class postSerializer(Serializers.ModelSerializer):
    query = Post.objects.all()
    class Meta:
        model = Post
        fields = '__all__'