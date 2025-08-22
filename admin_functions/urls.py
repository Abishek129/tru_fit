from django.urls import path, include
from .views import BlogViewSet, TestimonialViewSet, CoachProfileViewSet, CoachCertificationViewSet, PlansViewSet, location_view, PriceAndPlans, RecommendCoachAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"testimonials", TestimonialViewSet, basename='testimonial')
router.register(r'coaches', CoachProfileViewSet, basename='coachprofile')
router.register(r'certifications', CoachCertificationViewSet, basename='coachcertification')
router.register(r"plans", PlansViewSet, basename= "plans")
urlpatterns = [
    path("", include(router.urls)),
    path("location/", location_view, name = "location"),
    path("planDetails/", PriceAndPlans.as_view(), name ="plans" ),
    path('recommend/', RecommendCoachAPIView.as_view(), name = "recommend"),
] 