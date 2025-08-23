from django.urls import path, include
from .views import BlogViewSet, TestimonialViewSet, CoachProfileViewSet, CoachCertificationViewSet, PlansViewSet, location_view, PriceAndPlans, RecommendCoachAPIView,RBuyNowAPIView, RPaymentInitializationView, RPaymentVerificationView
from rest_framework.routers import DefaultRouter
from .views import CBuyNowAPIView, CPaymentInitializationView, CPaymentVerificationView, CPaymentWebhookView, cashfree_webhook

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
    path('int-buy-now/', RBuyNowAPIView.as_view(), name = "buy-now-int"),
    path('int-payment-init/<int:client_id>/', RPaymentInitializationView.as_view(), name = 'payment-init-int'),
    path('int-payment-verify/', RPaymentVerificationView.as_view(), name = "payment-verify-int" ),
    path('ind-buy-now/', CBuyNowAPIView.as_view(), name = "ind-buy-now" ),
    path('ind-payment-init/<int:client_id>/', CPaymentInitializationView.as_view(), name = 'payment-init-ind'),
    path('ind-payment-verify/', CPaymentVerificationView.as_view(), name = "payment-verify-ind"),
    path("cashfree-webhook/", CPaymentWebhookView.as_view(), name = "cashfree-webhook"),
    path("cashfree-webhook2/",cashfree_webhook, name = 'webhook'),

] 