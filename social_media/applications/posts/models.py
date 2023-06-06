from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db import models
import uuid


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'/user_{instance.user.id}/{filename}'


class Tag(models.Model):
    title = models.TextField(max_length=16, verbose_name='Tag')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('Tag', args=[self.slug])

    # Define save method for saving tag
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


# Define class for displaying stream of posts among users (a stream of post from following to follower)
class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    # define function to create streams after each post saves
    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post')


# Get signal of saving a post then do stuff
# Stream
post_save.connect(Stream.add_post, sender=Post)
