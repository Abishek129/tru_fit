from django.urls import path, include
from .views import BlogViewSet, TestimonialViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"testimonials", TestimonialViewSet, basename='testimonial')
urlpatterns = [
    path("", include(router.urls)),
] 