# admin_functions/serializers.py
from rest_framework import serializers
from .models import Blog, Testimonial

class BlogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    content_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "image",
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
            
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image and request else None