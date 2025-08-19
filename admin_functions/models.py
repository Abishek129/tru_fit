from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta


from django.core.files.storage import FileSystemStorage
from PIL import Image
import os

def user_image_path(instance, filename):
    gmail = instance.email.split('@')[0]
    return f'dp/{gmail}/{filename}'
# ================================
# User Manager
# ================================
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Important for Google Sign-In
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# ================================
# User Model
# ================================
class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    ]
    
    email = models.EmailField(unique=True)
    firebase_uid = models.CharField(max_length=128, unique=True, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)  # ✅ Replace first_name & last_name
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    reset_token = models.CharField(max_length=128, blank=True, null=True)
    reset_token_created_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

from django.db import models
from django.core.validators import FileExtensionValidator

class Blog(models.Model):
    title = models.CharField(max_length=300)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    # PDF upload only
    content = models.FileField(
        upload_to='blog_pdfs/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def content_filename(self):
        return self.content.name.split('/')[-1] if self.content else ""
    





class Testimonial(models.Model):
    client_name = models.CharField(max_length=300)
    image = models.ImageField(upload_to='testimonial_images/', blank=True, null=True)
    # PDF upload only
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.client_name




