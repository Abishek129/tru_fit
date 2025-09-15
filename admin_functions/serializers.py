# admin_functions/serializers.py
from rest_framework import serializers
from .models import Blog, Testimonial, CoachProfile, CoachCertification, ClientDetails, Clinet_Coach, ActiveClient 

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


from django.db import transaction

class CoachProfileSerializer(serializers.ModelSerializer):
    certifications = CoachCertificationSerializer(many=True, required=False)

    class Meta:
        model = CoachProfile
        fields = [
            'id', 'name', 'image', 'gender', 'experience', 'coach_level',
            'intensity_level', 'specialties','tags','location', 'previous_work', 'approach','specializations','personality_traits',
            'bio', 'calendly_link', 'certifications', 'summary'
        ]

    def _normalize_certs(self, certs):
        if certs is None:
            return []
        if isinstance(certs, str):
            return [{'certificate': c.strip()} for c in certs.split(',') if c.strip()]
        out = []
        for c in certs:
            if isinstance(c, dict):
                name = c.get('certificate')
            else:
                name = str(c)
            if name:
                out.append({'certificate': name})
        return out

    @transaction.atomic
    def create(self, validated_data):
        # IMPORTANT: remove reverse relation from validated_data
        incoming_certs = validated_data.pop('certifications', None)

        # Also accept flexible formats from initial_data (e.g., CSV in multipart)
        if incoming_certs is None and hasattr(self, 'initial_data'):
            incoming_certs = self.initial_data.get('certifications')

        certs_data = self._normalize_certs(incoming_certs)

        coach = CoachProfile.objects.create(**validated_data)

        if certs_data:
            CoachCertification.objects.bulk_create([
                CoachCertification(coach=coach, **cd) for cd in certs_data
            ])
        return coach

    @transaction.atomic
    def update(self, instance, validated_data):
        # IMPORTANT: remove reverse relation from validated_data
        incoming_certs = validated_data.pop('certifications', None)

        # Update simple fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        # Allow replacing certifications if provided (including CSV via initial_data)
        if incoming_certs is None and hasattr(self, 'initial_data'):
            # Only replace if the client explicitly sent the key
            if 'certifications' in self.initial_data:
                incoming_certs = self.initial_data.get('certifications')

        if incoming_certs is not None:
            instance.certifications.all().delete()
            certs_data = self._normalize_certs(incoming_certs)
            if certs_data:
                CoachCertification.objects.bulk_create([
                    CoachCertification(coach=instance, **cd) for cd in certs_data
                ])

        return instance


from .models import ClientDetails, Clinet_Coach, CoachProfile  # adjust import path

# --- Nested mini serializers (read-only) ---

class CoachMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachProfile
        fields = ["id", "name"]


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
    """
    Use this for list/detail responses. Shows nested minimal info.
    """
    client = ClientMiniSerializer(source="client", read_only=True)
    coach = CoachMiniSerializer(source="coach", read_only=True)

    # Handy computed fields (optional)
    client_name = serializers.CharField(source="client.name", read_only=True)
    coach_name  = serializers.CharField(source="coach.name", read_only=True)

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "client",        # nested mini
            "coach",         # nested mini
            "client_name",   # quick access
            "coach_name",    # quick access
            "start_date",
            "duration_weeks",
            "active",
            "us_revenue",
            "inr_revenue",
        ]

class CoachRevenueSerializer(serializers.ModelSerializer):  
    coach = CoachMiniSerializer(source = 'coach', read_only=True)
    client = ClientMiniSerializer(source = 'client', read_only=True)

    class Meta:
        model = Clinet_Coach
        fields = [
            "id",
            "coach",
            "client",
            "inr_revenue",
            "us_revenue",
        ]



class CoachTableSerializer(serializers.ModelSerializer):
    coach = CoachMiniSerializer(source = 'coach',read_only=True)
    client = ClientMiniSerializer(source = 'client',read_only=True)
    
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
        fields = ["email", "password", "name", "phone_number", "user_type"]
        extra_kwargs = {"user_type": {"required": False}}

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
    

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login with email + password (your USERNAME_FIELD is email).
    Adds basic fields into token (optional).
    """
    username_field = User.EMAIL_FIELD if hasattr(User, "EMAIL_FIELD") else "email"

    def validate(self, attrs):
        # Accept either "email" or "username" in payload; map to email.
        email = attrs.get("email") or attrs.get("username")
        password = attrs.get("password")

        if not email or not password:
            raise AuthenticationFailed("Email and password are required.")

        user = authenticate(
            request=self.context.get("request"),
            username=email,  # ModelBackend uses USERNAME_FIELD internally
            password=password,
        )
        if not user:
            raise AuthenticationFailed("Invalid credentials.")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        self.user = user
        data = super().validate({"username": email, "password": password})

        # optional: include small profile in response
        data.update({
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_staff": user.is_staff,
                "user_type": user.user_type,
            }
        })
        return data
    


class AdminOnlyTokenObtainPairSerializer(EmailTokenObtainPairSerializer):
    """
    Same as login but enforces is_staff True.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_staff:
            raise AuthenticationFailed("Admin access only.")
        return data