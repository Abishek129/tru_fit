from django.urls import path, include
from .views import BlogViewSet, TestimonialViewSet, CoachProfileViewSet, CoachCertificationViewSet, PlansViewSet, location_view, PriceAndPlans, RecommendCoachAPIView,RBuyNowAPIView, RPaymentInitializationView, RPaymentVerificationView
from rest_framework.routers import DefaultRouter
from .views import CBuyNowAPIView, CPaymentInitializationView, CPaymentVerificationView, CPaymentWebhookView, CashfreeWebhookView, SignupView, LoginView, AdminLoginView, RefreshView, LogoutView, CategoryViewSet, ClinetCoachTableViewSet, TestEmailView, ClientTableView, CoachClientListView, UserProfileView, TopClientsByPaymentMode, ClientCoachStatsView
from .views import ForgotPasswordRequestView, VerifyOTPView, CoachRevenueView , NewSignupsDomesticView, CoachSummaryView, NewSignupsIntView , FinanceAmountByLocationView, CoachMiniListView, CoachStatusUpdateView, LeadsListView, LeadCaptureView, CoachCountView, TestImageViewSet, CoachCreateView, test_socket_view, NotificationListView, NotificationEditView, NotificationView, EnquiryFormView
from .views import coach_profile_list, coach_profile_detail, CPaymentTestView,CashfreeWebhookView, SendLeadsEmailView, NotificationTestView, ClientsCheckView

from .views import testimonial_list, testimonial_detail, payment_webhook, run_simple_task , payment_webhook_test, testMailView
from .views import CoachClientView, CoachRevenueChangeView
from .views import ClientCheck2View, FinanceCheck
router = DefaultRouter()
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"testimonials", TestimonialViewSet, basename='testimonial')
router.register(r"test-images", TestImageViewSet, basename="testimage")
router.register(r'coaches', CoachProfileViewSet, basename='coachprofile')
router.register(r'certifications', CoachCertificationViewSet, basename='coachcertification')
router.register(r"plans", PlansViewSet, basename= "plans")
router.register(r"client_coach_change", CoachClientView, basename='client_coach_change')
router.register(r"coach_revenue_adjust", CoachRevenueChangeView, basename='coach_revnue_change')
router.register(r'client-coach', ClinetCoachTableViewSet, basename='client-coach')
router.register(r'finance_update', FinanceCheck, basename="finance_update")  
urlpatterns = [
    path("", include(router.urls)),
    path("location/", location_view, name = "location"),
    path("planDetails/", PriceAndPlans.as_view(), name ="plans" ),
    path('recommend/', RecommendCoachAPIView.as_view(), name = "recommend"),
    path('create/category/', CategoryViewSet.as_view({'post': 'create', 'get':'list'}), name='create-category'),
    path('int-buy-now/', RBuyNowAPIView.as_view(), name = "buy-now-int"),
    path('int-payment-init/<int:client_id>/', RPaymentInitializationView.as_view(), name = 'payment-init-int'),
    path('int-payment-verify/', RPaymentVerificationView.as_view(), name = "payment-verify-int" ),
    path('ind-buy-now/', CBuyNowAPIView.as_view(), name = "ind-buy-now" ),
    path('ind-payment-init/<int:client_id>/', CPaymentInitializationView.as_view(), name = 'payment-init-ind'),
    path('ind-payment-verify/', CPaymentVerificationView.as_view(), name = "payment-verify-ind"),
    path("cashfree-webhook/", CPaymentWebhookView.as_view(), name = "cashfree-webhook"),
    
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
    path('coachList/', CoachMiniListView.as_view(), name='coach-list'), # change name
    path('coach_status/<int:coach_id>/', CoachStatusUpdateView.as_view(), name='coach-status-update'),
    path('leads/', LeadsListView.as_view(), name='leads-list'),
    path('capture-lead/', LeadCaptureView.as_view(), name='lead-capture'),
    path('coach-count/', CoachCountView.as_view(), name='coach-count'),
    path('create-coach/', CoachCreateView.as_view(), name='create-coach'),
    path('test-socket/', test_socket_view, name='test-socket'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('new-notifications/', NotificationView.as_view(), name='notifications'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/', NotificationEditView.as_view(), name='notification-edit'),
    path('recent-clients/', TopClientsByPaymentMode.as_view(), name='top-clients'),
    path('enquiry/', EnquiryFormView.as_view(), name='enquiry-form'),
    path('stats/', ClientCoachStatsView.as_view(), name='stats'),
    

    # =================== Test Celery Task ===================
    path('run-simple-task/', run_simple_task, name='run-simple-task'),
    # =============== Payment Test Api ==============
    path('cashfree-payment-test/', CPaymentTestView.as_view(), name='cashfree-payment-test'),

    # =============== Webhook Apis ==================
    path('payment-webhook-test/', payment_webhook_test, name='payment-webhook-razorpay-test'),
    #('test-cashfree-webhook/', CashfreeWebhookView.as_view(), name='test-webhook'),
    path('paymenthandler2/', payment_webhook, name='paymenthandler'),
    path("cashfree-webhook2/",CashfreeWebhookView.as_view(), name = 'webhook'),
    # =============== Client's Apis ==============
    path('coach-profiles/', coach_profile_list, name='coach-profile-list'),
    path('coach-profiles/<int:coach_id>/', coach_profile_detail, name='coach-profile-detail'),
    path('testimonials-get/', testimonial_list, name='testimonial-list'),
    path('testimonials-get/<int:pk>/', testimonial_detail, name='testimonial-detail'),
    path('test-mail-view/', testMailView.as_view(), name='test-mail-view'),

    # =================== Admin Tasks ===================
    path('leads/send-mail/', SendLeadsEmailView.as_view(), name='send-lead-emails'),
    path('notification-test/', NotificationTestView.as_view(), name='notification-test'),
    path('clients_check/', ClientsCheckView.as_view(), name="client_check"),
    path('finance_details_check/', ClientCheck2View.as_view(), name = 'finance_check')


    
    
  

] 

