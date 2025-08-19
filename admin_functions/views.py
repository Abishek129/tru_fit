from django.shortcuts import render

# Create your views here.

# admin_functions/views.py
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Blog, Testimonial
from .serializers import BlogSerializer, TestimonialSerializer
from rest_framework.permissions import AllowAny

class BlogViewSet(viewsets.ModelViewSet):
    """
    CRUD for Blog with file upload support.
    """
    permission_classes = [AllowAny]
    queryset = Blog.objects.order_by("-created_at")
    serializer_class = BlogSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # handle image/pdf uploads


class TestimonialViewSet(viewsets.ModelViewSet):
    """
    CRUD for Blog with file upload support.
    """
    permission_classes = [AllowAny]
    queryset = Testimonial.objects.order_by("-created_at")
    serializer_class = TestimonialSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # handle image/pdf uploads

