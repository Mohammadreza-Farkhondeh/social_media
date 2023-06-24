from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from posts.models import Post
from PIL import Image
import os


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    avatar_name = f'user_{instance.user.id}/avatar.jpg'

    full_path = os.path.join(settings.MEDIA_ROOT, avatar_name)
    if os.path.exists(full_path):  # Check if it exists, if yes, then delete the old photo
        os.remove(full_path)

    return full_path

# Profile class has OneToOne relationship with User model that is default_AUTH-model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=12, null=True, blank=True)
    last_name = models.CharField(max_length=12, null=True, blank=True)
    url = models.CharField(max_length=80, null=True, blank=True)
    profile_info = models.TextField(max_length=150, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    favorites = models.ManyToManyField(Post)
    avatar = models.ImageField(upload_to=user_directory_path,blank=True, null=True, verbose_name='Picture')

    # Override the save() method to resize the image
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
        except:
            pass

    def __str__(self):
        return self.user.username


# Signal receiver functions that creates a profile instance when a user instance is created
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
