from django.urls import path, include
from .views import BlogViewSet, TestimonialViewSet, CoachProfileViewSet, CoachCertificationViewSet, PlansViewSet, location_view, PriceAndPlans, RecommendCoachAPIView,RBuyNowAPIView, RPaymentInitializationView, RPaymentVerificationView
from rest_framework.routers import DefaultRouter
from .views import CBuyNowAPIView, CPaymentInitializationView, CPaymentVerificationView, CPaymentWebhookView, CashfreeWebhookView, SignupView, LoginView, AdminLoginView, RefreshView, LogoutView, CategoryViewSet, ClinetCoachTableViewSet, TestEmailView, ClientTableView, CoachClientListView 
from .views import ForgotPasswordRequestView, VerifyOTPView, CoachRevenueView , NewSignupsDomesticView, CoachSummaryView, NewSignupsIntView , FinanceAmountByLocationView, CoachMiniListView, CoachStatusUpdateView, LeadsListView, LeadCaptureView

router = DefaultRouter()
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"testimonials", TestimonialViewSet, basename='testimonial')
router.register(r'coaches', CoachProfileViewSet, basename='coachprofile')
router.register(r'certifications', CoachCertificationViewSet, basename='coachcertification')
router.register(r"plans", PlansViewSet, basename= "plans")
router.register(r'client-coach', ClinetCoachTableViewSet, basename='client-coach')  
urlpatterns = [
    path("", include(router.urls)),
    path("location/", location_view, name = "location"),
    path("planDetails/", PriceAndPlans.as_view(), name ="plans" ),
    path('recommend/', RecommendCoachAPIView.as_view(), name = "recommend"),
    path('create/category/', CategoryViewSet.as_view({'post': 'create', 'get':'list'}), name='create-category'),
    path('int-buy-now/', RBuyNowAPIView.as_view(), name = "buy-now-int"),
    path('int-payment-init/<int:client_id>/<int:coach_id>/', RPaymentInitializationView.as_view(), name = 'payment-init-int'),
    path('int-payment-verify/', RPaymentVerificationView.as_view(), name = "payment-verify-int" ),
    path('ind-buy-now/', CBuyNowAPIView.as_view(), name = "ind-buy-now" ),
    path('ind-payment-init/<int:client_id>/', CPaymentInitializationView.as_view(), name = 'payment-init-ind'),
    path('ind-payment-verify/', CPaymentVerificationView.as_view(), name = "payment-verify-ind"),
    path("cashfree-webhook/", CPaymentWebhookView.as_view(), name = "cashfree-webhook"),
    path("cashfree-webhook2/",CashfreeWebhookView.as_view(), name = 'webhook'),
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/token/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("send-test-email/", TestEmailView.as_view(), name="send_test_email"),  
    path("client-table/", ClientTableView.as_view(), name="client-table"),
    path("client-table/<slug:start_date>/", ClientTableView.as_view(), name="client-table-start"),
    path("client-table/<slug:start_date>/<slug:end_date>/", ClientTableView.as_view(), name="client-table-range"),
    path("coaches/<int:coach_id>/relations/", CoachClientListView.as_view(), name="coach-client-list"),
    path('forgot-password/', ForgotPasswordRequestView.as_view(), name='forgot-password-request'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('coach-revenue/<int:coach_id>/', CoachRevenueView.as_view(), name='coach-revenue'),
    path('signups-domestic/', NewSignupsDomesticView.as_view(), name='finance-domestic'),
    path('signups-international/', NewSignupsIntView.as_view(), name='finance-international'),
    path('finance/', FinanceAmountByLocationView.as_view(), name='finance-by-location'),
    path('coach/summary/', CoachSummaryView.as_view(), name='coach-summary'),
    path('coachList/', CoachMiniListView.as_view(), name='coach-list'),
    path('coach_status/<int:coach_id>/', CoachStatusUpdateView.as_view(), name='coach-status-update'),
    path('leads/', LeadsListView.as_view(), name='leads-list'),
    path('capture-lead/', LeadCaptureView.as_view(), name='lead-capture'),
    
    
    #path('revenue-summary/', RevenueSummaryView.as_view(), name='revenue-summary'),

    

] 