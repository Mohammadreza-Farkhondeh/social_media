from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db import models
import uuid


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'/user_{instance.user.id}/{filename}'


# Define Tag model for its usage in post model
class Tag(models.Model):
    title = models.TextField(max_length=16, verbose_name='Tag')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('Tag', args=[self.slug])

    # Override save method for saving tag (consider if there is no slug)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Define class of postContent model to save file location and its owner
class PostContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_owner')
    file = models.FileField(upload_to=user_directory_path)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ManyToManyField(PostContent, related_name='contents')
    caption = models.TextField(max_length=1500, verbose_name='Caption')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tags')
    likes = models.IntegerField(default=0)
    posted = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('post', args=[str(self.id)])

    def __str__(self):
        return str(self.id)


# Define class for displaying relations of following between two users
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='following')


# A model for displaying who likes which post in each row
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post')


# A model for recommendations in explore page
class Recommendation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation')
    posts = models.ManyToManyField(Post)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'Recommendation for {self.user.email}'
