# admin_functions/serializers.py
from rest_framework import serializers
from .models import Blog, Testimonial, CoachProfile, CoachCertification, ClientDetails

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


class CoachMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachProfile
        fields = ["id", "name", "coach_level", "image"]


class ClientDetailsSerializer(serializers.ModelSerializer):
    # write: coach as PK; read: include nested details too
    coach = serializers.PrimaryKeyRelatedField(queryset=CoachProfile.objects.all())
    coach_detail = CoachMiniSerializer(source="coach", read_only=True)

    # nice-to-have display labels for choices
    payment_mode_display = serializers.CharField(source="get_payment_mode_display", read_only=True)
    plan_display = serializers.CharField(source="get_plan_display", read_only=True)

    class Meta:
        model = ClientDetails
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "coach",            # send coach id when creating/updating
            "coach_detail",     # nested coach info in responses
            "residence",
            "created_date",     # read-only (auto filled)
            "payment_mode",
            "payment_mode_display",
            "plan",
            "plan_display",
        ]
        read_only_fields = ["created_date"]



from rest_framework import serializers
from .models import Plans

class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = [
            'id',
            'category',            # returns stored value e.g. "junior"
            'location',            # returns stored value e.g. "international"
            'short_term_price',
            'long_term_price',
            'consultation_call_price',
        ]

