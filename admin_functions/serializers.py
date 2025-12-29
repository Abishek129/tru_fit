# admin_functions/serializers.py
from rest_framework import serializers
from .models import Blog, Testimonial, CoachProfile, CoachCertification, ClientDetails, Clinet_Coach, ActiveClient , Finance_details




from .models import User



class UserSerializer(serializers.ModelSerializer):
    #image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email","image", "name", "phone_number",  "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]

    


class BlogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    content_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "image",
            "tag",
            "content",       # PDF file
            "image_url",
            "content_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image and request else None

    def get_content_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.content.url) if obj.content and request else None



class TestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "client_name",
            "image",
            "body",      
            "image_url",
            "age",
            "tags",
            
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image and request else None
    



class CoachCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachCertification
        fields = ['id', 'certificate']


from .models import CoachProfile, CoachCertification
from django.db import transaction

class CoachProfileSerializer(serializers.ModelSerializer):
    certifications = CoachCertificationSerializer(many=True, required=False)

    class Meta:
        model = CoachProfile
        fields = [
            'id', 'name', 'image', 'gender', 'experience', 'coach_level','status',
            'tags','location', 'previous_work', 'approach','specializations','linkedin_link',
            'insta_link', 'experience_details',
            'bio', 'calendly_link', 'certifications', 'summary', 'spurfit_url'
        ]

    def _normalize_certs(self, certs):
        if certs is None:
            return []
        if isinstance(certs, str):
            return [{'certificate': c.strip()} for c in certs.split(',') if c.strip()]
        out = []
        for c in certs:
            name = c.get('certificate') if isinstance(c, dict) else str(c)
            if name:
                out.append({'certificate': name})
        return out

    @transaction.atomic
    def create(self, validated_data):
        incoming_certs = validated_data.pop('certifications', None)

        # ADD THIS: fall back to raw input if DRF dropped the field
        if incoming_certs is None and hasattr(self, 'initial_data') and 'certifications' in self.initial_data:
            incoming_certs = self.initial_data.get('certifications')

        coach = super().create(validated_data)

        certs_data = self._normalize_certs(incoming_certs)
        if certs_data:
            CoachCertification.objects.bulk_create(
                [CoachCertification(coach=coach, **cd) for cd in certs_data]
            )
        return coach

    @transaction.atomic
    def update(self, instance, validated_data):
        incoming_certs = validated_data.pop('certifications', None)

        # handle image updates (and allow clearing)
        image = validated_data.pop('image', serializers.empty)
        for k, v in validated_data.items():
            setattr(instance, k, v)

        if image is not serializers.empty:
            if image in (None, "", "null"):
                instance.image.delete(save=False)
                instance.image = None
            else:
                instance.image = image

        instance.save()

        if incoming_certs is None and hasattr(self, 'initial_data') and 'certifications' in self.initial_data:
            incoming_certs = self.initial_data.get('certifications')

        if incoming_certs is not None:
            instance.certifications.all().delete()
            certs_data = self._normalize_certs(incoming_certs)
            if certs_data:
                CoachCertification.objects.bulk_create(
                    [CoachCertification(coach=instance, **cd) for cd in certs_data]
                )
        return instance


from .models import ClientDetails, Clinet_Coach, CoachProfile, CoachRevenue  # adjust import path

# --- Nested mini serializers (read-only) ---

class CoachMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachProfile
        fields = ["id", "name", "coach_level", "status"]


class ClientMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDetails
        fields = ["id", "name", "email", "phone_number", "created_date"]


# --- Main serializers ---

class ClientDetailsSerializer(serializers.ModelSerializer):
    # created_date should be read-only; choices are validated by DRF automatically
    created_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClientDetails
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "residence",
            "coach",
            "created_date",
            'payment_date',
            "payment_mode",
            "plan",
            "payment_status",
        ]
class ClientCoachReadSerializer(serializers.ModelSerializer):
    client = ClientMiniSerializer(read_only=True)  # remove source="client"
    coach  = CoachMiniSerializer(read_only=True)   # remove source="coach"

    client_name = serializers.CharField(source="client.name", read_only=True)
    coach_name  = serializers.CharField(source="coach.name", read_only=True)

    class Meta:
        model = Clinet_Coach
        fields = [
            "id", "client", "coach", "client_name", "coach_name",
            "start_date", "duration_weeks", "active", "us_revenue", "inr_revenue",
        ]

class CoachRevenueSerializer(serializers.ModelSerializer):
    coach = CoachMiniSerializer(read_only=True)

    class Meta:
        model = CoachRevenue
        fields = ["id", "coach", "us_revenue", "inr_revenue"]


class CoachTableSerializer(serializers.ModelSerializer):
    coach = CoachMiniSerializer(read_only=True)   # ← remove source=
    client = ClientMiniSerializer(read_only=True) # ← remove source=

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "coach",
            "client",
            "start_date",
            "duration_weeks",
            "active",
            "inr_revenue",
            "us_revenue",
        ]

class ClinetCoachTableSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    client_email = serializers.EmailField(source="client.email", read_only=True)
    client_residence = serializers.CharField(source="client.residence", read_only=True)
    coach_name = serializers.CharField(source="coach.name", read_only=True)

    # Custom field for duration
    duration_weeks = serializers.SerializerMethodField()

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "client_name",
            "client_email",
            "client_residence",
            "coach_name",
            "start_date",
            "duration_weeks",
        ]

    def get_duration_weeks(self, obj):
        if obj.duration_weeks:
            return f"{obj.duration_weeks} weeks"
        return None


class ClientTableSerializer(serializers.ModelSerializer):
    coach = CoachMiniSerializer(read_only=True)

    class Meta:
        model = ClientDetails
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "residence",
            "state",
            "city",
            "coach",
            "created_date",
            'payment_date',
            'active',
            "payment_mode",
            "plan",
            "payment_status",
        ]


class CoachRevenueSerializer(serializers.ModelSerializer):
    coach = CoachMiniSerializer(read_only=True)

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "coach",
            "inr_revenue",
            "us_revenue",
        ]


class CoachSummarySerializer(serializers.ModelSerializer):
    total_clients  = serializers.IntegerField(read_only=True)
    active_clients_count = serializers.IntegerField(read_only=True)
    inr_revenue    = serializers.DecimalField(
        max_digits=30, decimal_places=2, read_only=True, source="revenues.inr_revenue"
    )
    us_revenue     = serializers.DecimalField(
        max_digits=30, decimal_places=2, read_only=True, source="revenues.us_revenue"
    )

    class Meta:
        model = CoachProfile
        fields = (
            "id", "name", "coach_level", "status",
            "total_clients", "active_clients_count",
            "inr_revenue", "us_revenue",
        )
            
class ActiveClientSerializer(serializers.ModelSerializer):
    # Nested read-only
    client = serializers.StringRelatedField(read_only=True)
    coach = serializers.StringRelatedField(read_only=True)

    # IDs for write
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=ClientDetails.objects.all(), source="client", write_only=True
    )
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=CoachProfile.objects.all(), source="coach", write_only=True
    )

    start_date = serializers.DateField()
    end_date = serializers.DateField()

    class Meta:
        model = ActiveClient
        fields = [
            "id",
            "client", "coach",       # nested (read-only)
            "client_id", "coach_id", # write-only
            "duration_weeks",
            "start_date",
            "end_date",
        ]

    def validate(self, attrs):
        """Extra safety at serializer level (in addition to model.clean)."""
        start_date = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end_date = attrs.get("end_date") or getattr(self.instance, "end_date", None)

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError("End date must be after start date.")
        return attrs
    
    
from rest_framework import serializers
from .models import Plan, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'coach_level', 'location']

class PlansSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Plan
        fields = [
            'id',
            'category',            # nested read-only
            'category_id',         # write-only for setting category
            'duration_weeks',
            'price',
            'name'
        ]
        extra_kwargs = {
            'duration_weeks': {'validators': []},  # disable unique_together validator
        }

    def validate(self, attrs):
        category = attrs.get('category') or getattr(self.instance, 'category', None)
        duration_weeks = attrs.get('duration_weeks') or getattr(self.instance, 'duration_weeks', None)

        if category and duration_weeks:
            exists = Plan.objects.filter(category=category, duration_weeks=duration_weeks)
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise serializers.ValidationError(
                    "A plan with this category and duration already exists."
                )
        return super().validate(attrs)
    




from django.contrib.auth import get_user_model, authenticate
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "name", "phone_number", ]
        

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Fallback: name from email if not provided
        if not validated_data.get("name"):
            validated_data["name"] = slugify(validated_data["email"].split("@")[0]).replace("-", " ").title()
        user = User.objects.create_user(password=password, **validated_data)
        user.is_staff = True
        user.save()
        return user

    def to_representation(self, instance):
        # return tokens on signup
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data.update({
            "id": instance.id,
            "is_staff": instance.is_staff,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
        return data
    
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Your custom User has USERNAME_FIELD = "email"
# AbstractBaseUser already works with that.
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login with email + password.
    """
    # Make sure SimpleJWT uses 'email' as the username field:
    username_field = "email"

    def validate(self, attrs):
        # Accept either "email" or "username" key in the request payload
        email = attrs.get("email") or attrs.get("username")
        password = attrs.get("password")

        if not email or not password:
            raise AuthenticationFailed("Email and password are required.")

        # ModelBackend will accept 'username' arg too, but email is fine
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            raise AuthenticationFailed("Invalid credentials.")
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        self.user = user

        # IMPORTANT: pass the key matching self.username_field
        data = super().validate({self.username_field: email, "password": password})

        # optional: include small profile in response
        data.update({
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_staff": user.is_staff
               
            }
        })
        return data


class AdminOnlyTokenObtainPairSerializer(EmailTokenObtainPairSerializer):
    """Same as login but enforces is_staff True."""
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_staff:
            raise AuthenticationFailed("Admin access only.")
        return data
    

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils import timezone
from .models import PasswordResetOTP
import random

User = get_user_model()

def generate_otp(n=6):
    # 6-digit numeric OTP
    return ''.join(str(random.randint(0, 9)) for _ in range(n))

class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    #new_password = serializers.CharField(min_length=6, write_only=True)

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        if not self.user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        return value

    def create(self, validated_data):
        user = self.user
        #new_password = validated_data['new_password']

        # If there is an existing active token, mark it used to avoid uniqueness conflicts
        PasswordResetOTP.objects.filter(user=user, used=False).update(used=True)

        otp = generate_otp(6)
        reset_obj = PasswordResetOTP.create_new(user, otp, ttl_minutes=10)

        # Send email (assumes EMAIL settings configured)
        from django.core.mail import send_mail
        send_mail(
            subject="Your password reset OTP",
            message=f"Hi {user.name or 'there'},\n\nYour OTP is: {otp}\nThis code expires in 10 minutes.\n\nIf you did not request this, please ignore.",
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            fail_silently=False,
        )
        return {"detail": "OTP sent to email."}


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs['email']
        otp = attrs['otp']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No account found with this email."})

        now = timezone.now()
        try:
            record = PasswordResetOTP.objects.get(user=user, used=False)
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp": "No active OTP found. Please request a new one."})

        if record.expires_at < now:
            raise serializers.ValidationError({"otp": "OTP has expired. Please request a new one."})
        if record.otp != otp:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        self.user = user
        self.record = record
        return attrs

    def save(self, **kwargs):
        # Set user's password to the already-hashed temp password
        user = self.user
        record = self.record
        user.password = record.temp_password_hashed  # already hashed via make_password
        user.save(update_fields=['password'])

        record.used = True
        record.save(update_fields=['used'])

        return {"detail": "Password has been reset successfully."}



class FinancialReportSerializer(serializers.Serializer):
    client = ClientMiniSerializer(read_only=True)
    
    class Meta:
        model = Finance_details
        fields = [
            "id",
            "client",
            'start_date',
            'end_date',
            "location",
            "amount_paid",
            "payment_status"
        
        ]


from rest_framework import serializers

class FinanceUpdateSerializer(serializers.ModelSerializer):
    # use client id for write operations
    client = serializers.PrimaryKeyRelatedField(
        queryset=ClientDetails.objects.all()
    )
    # if you still want the mini nested client for reads, add:
    # client_detail = ClientMiniSerializer(source='client', read_only=True)

    class Meta:
        model = Finance_details
        fields = [
            "id",
            "client",           # or "client_detail" as extra
            "start_date",
            "end_date",
            "location",
            "amount_paid",
            "payment_status",
            

        ]

from .models import Leads


class LeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = ['id', 'name', 'email', 'phone_number', 'messaged', 'created_at']
        extra_kwargs = {
            'email': {'validators': []},  
        }

    def create(self, validated_data):
        email = validated_data['email']
        
        existing_obj = Leads.objects.filter(email=email).first()
        
        if existing_obj:
            # Update fields manually
            for field, value in validated_data.items():
                setattr(existing_obj, field, value)
            
            # Override created_at with current timestamp
            existing_obj.created_at = timezone.now()
            existing_obj.save()
            return existing_obj
        
        # If object not found, create new
        return super().create(validated_data)


import uuid
from io import BytesIO
from pathlib import Path
from PIL import Image
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import TestImage

class TestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestImage
        fields = ["id", "image"]

    def create(self, validated_data):
        uploaded = validated_data.pop("image", None)
        obj = TestImage(**validated_data)

        if uploaded:
            img = Image.open(uploaded)
            # ensure a consistent mode for saving (handles PNG/WEBP with alpha)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # resize
            max_size = (800, 800)
            try:
                resample = Image.Resampling.LANCZOS  # Pillow >= 9.1
            except AttributeError:
                resample = Image.LANCZOS
            img.thumbnail(max_size, resample)

            # buffer -> JPEG (or keep original format if you want)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=85)
            buf.seek(0)

            # unique name
            stem = Path(uploaded.name).stem
            name = f"test_images/{uuid.uuid4().hex}_{stem}.jpg"

            obj.image.save(name, ContentFile(buf.read()), save=False)

        obj.save()
        return obj
    

from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'read']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'read': {'default': False},
        }


class TopClientsSerializer(serializers.ModelSerializer):
    coach_name  = serializers.CharField(source="coach.name", read_only=True)

    class Meta:
        model = ClientDetails
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "created_date",
            "plan",
            "city",
            "state",
            "payment_date",
            "coach",
            "coach_name",
            "residence"
        ]



class ClientCoachSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    coach_name  = serializers.CharField(source="coach.name", read_only=True)

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "client_name",
            "coach_name",
            "start_date",
            "duration_weeks",
            "active",
            "inr_revenue",
            "us_revenue",
        ]


class CoachRevenueSerializer(serializers.ModelSerializer):
    coach_name  = serializers.CharField(source="coach.name", read_only=True)

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "coach_name",
            "inr_revenue",
            "us_revenue",
        ]



class NewFinanceDetailsSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_email = serializers.EmailField(source='client.email', read_only=True)
    client_phone_number = serializers.CharField(source='client.phone_number', read_only=True)

    coach_name = serializers.CharField(source='coach.name', read_only=True)

    

    class Meta:
        model = Finance_details
        fields = [
            'client_name',
            'client_email',
            'client_phone_number',
            'coach_name',
            'location',
            'country',
            'payment_status',
            'created_date',
            'plan',
        ]


class ClientTable2Serializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='name', read_only=True)
    coach_name = serializers.CharField(source='coach.name', read_only=True)

    class Meta:
        model = ClientDetails
        fields = [
            'client_name',
            'email',
            'phone_number',
            'coach_name',
            'residence',
            'state',
            'city',
            'payment_date',
            'plan',
            'payment_status'
        ]


from rest_framework import serializers
from .models import ClientDetails

class ClientDetailsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDetails
        fields = [
            "name",
            "email",
            "phone_number",
            "coach",
            "residence",
            "state",
            "city",
            "payment_date",
            "plan",
            "payment_status",
            "active",
        ]
