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
    name = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to='admin_dp/', blank=True, null=True)
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
    tag = models.CharField(max_length=300, blank=True, null=True)
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
    age = models.CharField(max_length=20, blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.client_name



class CoachProfile(models.Model):
    COACH_LEVEL_CHOICES = [
        ('junior', 'JUNIOR'),
        ('senior', 'SENIOR'),
        ('elite', 'ELITE'),
    ]
    GENDER_CHOICES = [
        ('male', 'MALE'),
        ('female', 'FEMALE'),
        ('others', 'OTHERS'),
    ]
    INTENSITY_CHOICES = [
        (1, 'Not intense'),
        (2, 'A little intense'),
        (3, 'Somewhat intense'),
        (4, 'Intense'),
        (5, 'Very intense'),
    ]
    status_choices = [
        ('active', 'ACTIVE'),
        ('soft', 'SOFT'),
        ('hard', 'HARD'),
    ]

    name = models.CharField(max_length=300)
    image = models.ImageField(upload_to='CoachProfile/', blank=True, null=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, blank= True, null= True)
    experience = models.DecimalField(max_digits=5, decimal_places=2)
    coach_level = models.CharField(max_length=13, choices=COACH_LEVEL_CHOICES)
    status = models.CharField(max_length=10, choices=status_choices, default='active')
    intensity_level = models.IntegerField(choices=INTENSITY_CHOICES, default=3)  # Added
    specializations = models.TextField(blank=True, null=True)
    specialties = models.JSONField(blank=True, null=True)  # For goals
    tags = models.CharField(max_length=200, blank=True, null=True)
    personality_traits = models.JSONField(blank=True, null=True)  # For style
    bio = models.TextField(blank=True, null=True)
    calendly_link = models.URLField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    
    approach = models.TextField(blank=True, null=True)
    previous_work = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null = True)

    def __str__(self):
        return self.name

class CoachCertification(models.Model):  # better to keep singular
    coach = models.ForeignKey(
        CoachProfile,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    certificate = models.CharField(max_length=100)  # 20 might be too short

    def __str__(self):
        return f"{self.coach.name} - {self.certificate}"
    


    

#from django.core.validators import RegexValidator
from django.utils import timezone


from django.core.validators import RegexValidator


class ClientDetails(models.Model):
    PAYMENT_CHOICES = [
        ('razorpay', 'RAZORPAY'),
        ('cashfree', 'CASHFREE'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    name = models.CharField(max_length=300)
    email = models.EmailField(max_length=300)
    phone_number = models.CharField(
        max_length=17,
        validators=[RegexValidator(r'^\+?\d{7,15}$', 'Enter a valid phone number.')]
    )
    coach = models.ForeignKey(
        CoachProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coach_clients'
    )
    residence = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now) 
    payment_date = models.DateField(default=timezone.now) # or auto_now_add=True
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    plan = models.PositiveSmallIntegerField()
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES, default="pending")
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Clinet_Coach(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name='client_coach_rel')
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='coach_clients_rel')
    start_date = models.DateField(default=timezone.now)
    duration_weeks = models.PositiveIntegerField(blank=True, null=True)
    active = models.BooleanField(default=False)
    us_revenue = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    inr_revenue = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('client', 'coach')

    def __str__(self):
        return f"{self.client.name} - {self.coach.name}"


class ActiveClient(models.Model):
    client = models.OneToOneField(ClientDetails, on_delete=models.CASCADE, related_name='active_client')
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='active_clients')
    duration_weeks = models.PositiveIntegerField( blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.client.name} - {self.coach.name} (Active)"

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date.')

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is called on save
        super().save(*args, **kwargs)

from django.core.validators import MinValueValidator
from decimal import Decimal



class Category(models.Model):
    COACH_LEVEL_CHOICES = [
        ('junior', 'JUNIOR'),
        ('senior', 'SENIOR'),   # normalized label case
        ('elite',  'ELITE'),
    ]
    LOCATION_CHOICES = [
        ('domestic',      'DOMESTIC'),
        ('international', 'INTERNATIONAL'),
    ]
    coach_level = models.CharField(max_length=12, choices=COACH_LEVEL_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['coach_level', 'location'],
                name='uniq_plan_category_location'
            )
        ]

    def __str__(self):
        # show human labels
        return f"{self.get_coach_level_display()} - {self.get_location_display()}"


class Plan(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=100, unique=True, blank=True, null=True)  
    duration_weeks = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], blank=True, null=True )
    description = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'duration_weeks'],
                name='uniq_plan_category_duration'
            )
        ]

    def __str__(self):
        return f"{self.category} - {self.duration_weeks} weeks - ${self.price}"
    

class CoachRevenue(models.Model):
    coach = models.OneToOneField(CoachProfile, on_delete=models.CASCADE, related_name='revenues')
    #month = models.DateField()  # Store the first day of the month
    us_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    inr_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)



    def __str__(self):
        return f"{self.coach.name}"


    
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_otps'
    )
    otp = models.CharField(max_length=6)
    #temp_password_hashed = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'otp']),
            models.Index(fields=['expires_at']),
        ]
        # One active token per user
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'used'],
                condition=models.Q(used=False),
                name='unique_active_reset_token_per_user'
            )
        ]

    @classmethod
    def create_new(cls, user, otp, ttl_minutes=10):
        now = timezone.now()
        return cls.objects.create(
            user=user,
            otp=otp,
            #temp_password_hashed=make_password(raw_temp_password),
            created_at=now,
            expires_at=now + timezone.timedelta(minutes=ttl_minutes),
            used=False,
        )



class Finance_details(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.SET_NULL, related_name='finance_details', null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    LOCATION_CHOICES = [
        ('domestic',      'DOMESTIC'),
        ('international', 'INTERNATIONAL'),
    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    

    def __str__(self):
        return f"{self.client.name} - {self.location} - {self.amount_paid}"
    


    

class Leads(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    #message = models.TextField(blank=True, null=True)
    messaged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


from django.db import models

class TestImage(models.Model):
    image = models.ImageField(upload_to="test_images/")

    def __str__(self):
        return f"Image {self.id}"
    


class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification {self.id} - {'Read' if self.read else 'Unread'}"
    
