from django.shortcuts import render
from .utils import send_test_message
# Create your views here.

# admin_functions/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Blog, Testimonial, CoachProfile, CoachCertification, ClientDetails, Plan, Category, Clinet_Coach, CoachRevenue, Finance_details
from .serializers import BlogSerializer, TestimonialSerializer, CoachProfileSerializer, CoachCertificationSerializer, ClientDetailsSerializer, PlansSerializer, ClientDetailsSerializer, CategorySerializer, ClinetCoachTableSerializer, ClientTableSerializer, CoachMiniSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .permissions import IsAuthenticatedAndStaff
from .models import Notification
from .serializers import NotificationSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
import re
from rest_framework import generics
from .serializers import UserSerializer

class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedAndStaff]

    def get_object(self):
        # Always operate on the logged-in user
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False   # safer than full delete (soft delete)
        user.save(update_fields=["is_active"])
        return Response({"message": "User account deactivated."}, status=status.HTTP_200_OK)

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




from rest_framework import viewsets, permissions, filters
from django.shortcuts import get_object_or_404




class CoachProfileViewSet(viewsets.ModelViewSet):
    queryset = CoachProfile.objects.all().order_by('id')
    serializer_class = CoachProfileSerializer
    parser_classes = (MultiPartParser, FormParser)  # force multipart

    def create(self, request, *args, **kwargs):
        print("FILES:", request.FILES)
        print("DATA:", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CoachCertificationViewSet(viewsets.ModelViewSet):
    """
    CRUD for CoachCertification.
    You can filter by coach with ?coach=<coach_id>
    """
    serializer_class = CoachCertificationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['id', 'certificate']

    def get_queryset(self):
        qs = CoachCertification.objects.select_related('coach').all().order_by('id')
        coach_id = self.request.query_params.get('coach')
        if coach_id:
            qs = qs.filter(coach_id=coach_id)
        return qs

    def perform_create(self, serializer):
        # supports POSTing {"coach": <id>, "certificate": "..."}
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

from rest_framework.views import APIView
from rest_framework.response import Response



from django.http import JsonResponse
from .utils import get_country_code  # assuming the function is in utils.py
import json
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def location_view(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        lat = data.get("latitude")
        lng = data.get("longitude")
        location = get_country_code(lat, lng)
        return JsonResponse({"ok": location, "lat": lat, "lng": lng})
    return JsonResponse({"detail": "Only POST"}, status=405)



class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for Blog with file upload support.
    """
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

class PlansViewSet(viewsets.ModelViewSet):
    """
    CRUD for Blog with file upload support.
    """
    permission_classes = [AllowAny]
    queryset = Plan.objects.all()
    serializer_class = PlansSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]


class PriceAndPlans(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        location = request.data.get('location')
        coach_level = request.data.get('coach_level')
        category = get_object_or_404(Category, coach_level=coach_level, location=location)  
        plans = Plan.objects.get(category = category)
        serializer = PlansSerializer(plans)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import recommend_coaches
from .serializers import CoachProfileSerializer
from django.db.models import Q

class RecommendCoachAPIView(APIView):
    def post(self, request):
        injury = request.data.get('injury')
        gender = request.data.get('gender')

        if injury:
            # want: coach_level != "junior" AND status != "hard"
            base = CoachProfile.objects.exclude(coach_level="junior").exclude(status="hard")

            if gender == "anyone":
                coaches = base
            else:
                with_gender = base.filter(gender=gender)
                # fallback if none: drop gender AND status constraint, keep only not-junior
                coaches = with_gender if with_gender.exists() else CoachProfile.objects.exclude(coach_level="junior")
        else:
            # want: coach_level == "junior" AND status != "hard"
            base = CoachProfile.objects.filter(coach_level="junior").exclude(status="hard")

            coaches = base if gender == "anyone" else base.filter(gender=gender)

        # Randomize order and select only 4 coaches
        coaches = coaches.order_by('?')[:4]

        serializer = CoachProfileSerializer(coaches, many=True)
        return Response(serializer.data)
    
from rest_framework.generics import ListAPIView
from rest_framework import generics

class CoachMiniListView(generics.ListAPIView):
    queryset = CoachProfile.objects.all()
    serializer_class = CoachMiniSerializer


class CoachStatusUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, coach_id):
        new_status = request.data.get("status")
        if new_status not in ["active", "soft", "hard"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        coach = get_object_or_404(CoachProfile, id=coach_id)
        coach.status = new_status
        coach.save()
        return Response({"message": "Status updated"}, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404

class RBuyNowAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            name = request.data.get('name')
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            plan = int(request.data.get('plan'))  # 3 or 6
            residence = request.data.get('residence')
            coach_id = request.data.get('coach')
            coach = get_object_or_404(CoachProfile, pk=coach_id)
            if ClientDetails.objects.filter(email=email).exists():
                client = ClientDetails.objects.get(email=email)
                client.payment_mode="razorpay"
                client.plan=plan
                client.coach = coach
                client.residence=residence
                client.payment_status="pending"
                client.save()
            
            else:
                client = ClientDetails.objects.create(
                    name=name,
                    email=email,
                    phone_number=phone_number,                # REQUIRED FK
                    residence=residence,
                    payment_mode="razorpay",     # fixed
                    plan=plan
                )
            #print(client)
            finance_details = Finance_details.objects.create(client=client, location="international")
            data = ClientDetailsSerializer(client).data
            return Response(data, status=status.HTTP_201_CREATED)

        except ValueError:
            return Response({"detail": "Invalid plan. Use 3 or 6."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        






from decimal import Decimal, InvalidOperation
import razorpay
from django.conf import settings

class RPaymentInitializationView(APIView):
    """
    Creates a Razorpay Order in USD for a given client (ClientDetails).
    """
    permission_classes = [AllowAny]

    def post(self, request, client_id):
        try:
            client = get_object_or_404(ClientDetails, id=client_id)

            print("working 1")
            # Block repeat payments
            if client.payment_status == "paid":
                return Response({"error": "Payment already completed for this client."},
                                status=status.HTTP_400_BAD_REQUEST)
            print("working 2")
            # Pricing lookup (coach level + 'international' plan row)
            print(client)
            coach_level = client.coach.coach_level   
            print(coach_level)     # 'junior' | 'senior' | 'elite'
            location = "international"
            cat = get_object_or_404(Category, coach_level=coach_level, location=location)
            print("working 3")
            # Amount (3 or 6 months)
            if client.plan == 1:
                plan = Plan.objects.get(category=cat, duration_weeks=None)
                amount_dec = plan.price
            elif client.plan == 2:
                plan = Plan.objects.get(category=cat, duration_weeks=12)
                if Clinet_Coach.objects.filter(client=client, coach=client.coach).exists():
                    active_client = Clinet_Coach.objects.get(client=client, coach=client.coach)
                    active_client.duration_weeks = 12
                    active_client.save()
                else:
                    active_client = Clinet_Coach.objects.create(client=client, coach=client.coach, duration_weeks=12, active = False)
                if not plan:
                    return Response({"error": "No plan found for the selected category and duration."}, status=status.HTTP_400_BAD_REQUEST)
                plan = Plan.objects.get(category=cat, duration_weeks=12)
                amount_dec = plan.price
            elif client.plan == 3:
                plan = Plan.objects.get(category=cat, duration_weeks=24)
                if Clinet_Coach.objects.filter(client=client, coach=client.coach).exists():
                    active_client = Clinet_Coach.objects.get(client=client, coach=client.coach)
                    active_client.duration_weeks = 12
                    active_client.save()
                else:
                    active_client = Clinet_Coach.objects.create(client=client, coach=client.coach, duration_weeks=12, active = False)
                #if not 
                #    return Response({"error": "No plan found for the selected category and duration."}, status=status.HTTP_400_BAD_REQUEST)
                #
                amount_dec = plan.price
                
            else:
                return Response({"error": "Invalid plan.", "client_plan":client.plan}, status=status.HTTP_400_BAD_REQUEST)
           
            print("working 4")
            # Razorpay client from env settings
            key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
            key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)
            if not key_id or not key_secret:
                return Response({"error": "Razorpay keys are not configured on the server."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            rz_client = razorpay.Client(auth=(key_id, key_secret))
            print("working 5")
            # USD: 2 decimal places → cents
            amount_minor = int((amount_dec * Decimal("100")).quantize(Decimal("1")))
            print(amount_minor)

            rz_order = rz_client.order.create({
                "amount": amount_minor,
                "currency": "USD",                     # USD-only
                "receipt": f"client_{client.id}",
                "payment_capture": 1,
                "notes": {
                    "client_id": str(client.id),
                    "client_email": client.email,
                    "plan_months": str(client.plan),
                    "coach_level": coach_level,
                    "pricing_location": location,
                }
            })

            # (Optional) save rz_order["id"] for later verification
            # client.razorpay_order_id = rz_order["id"]
            # client.save(update_fields=["razorpay_order_id"])

            return Response({
                "razorpay_order_id": rz_order["id"],
                "amount": rz_order["amount"],          # in cents
                "currency": rz_order["currency"],      # "USD"
                "key": key_id,
                "client": {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone_number": client.phone_number,
                    "plan": client.plan,
                    "coach_level": coach_level,
                    "location": location,
                }
            }, status=status.HTTP_200_OK)

        except razorpay.errors.BadRequestError as e:
            return Response({"error": "Razorpay BadRequestError", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except (InvalidOperation, ValueError) as e:
            return Response({"error": "Amount computation failed", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Unexpected error", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class RPaymentVerificationView(APIView):
    """
    Verifies Razorpay payment and updates the order status.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract payment details
        client_id = request.data.get("client_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        payment_id = request.data.get("razorpay_payment_id")
        signature = request.data.get("razorpay_signature")

        if not all([client_id, payment_id, signature]):
            return Response({"error": "Incomplete payment details provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order
        client_obj = get_object_or_404(ClientDetails, id=client_id)

        key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)        
        # Verify the Razorpay payment signature
        razorpay_client = razorpay.Client(auth=(key_id, key_secret))
        try:
            razorpay_client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )
            # Update the order's payment status
            
            
            client_obj.payment_status = "paid"
            
            client_obj.save(update_fields=["payment_status"])
            client_obj.payment_date = timezone.now()
            cat = Category.objects.get(coach_level=client_obj.coach.coach_level, location="international")
            if client_obj.plan == 2:
                    plan = Plan.objects.get(category=cat, duration_weeks=12)
                    order_amt = plan.price
            elif client_obj.plan == 3:
                plan = Plan.objects.get(category=cat, duration_weeks=24)
                order_amt = plan.price
            else:
                plan = Plan.objects.get(category=cat, duration_weeks=None)
                order_amt = plan.price
            
            if client_obj.plan != 1:
                client_obj.active = True
                active_client = Clinet_Coach.objects.get(client=client_obj,coach=client_obj.coach)
                
                if client_obj.plan == 2:
                    plan = Plan.objects.get(category=cat, duration_weeks=12)
                    order_amt = plan.price
                else:
                    plan = Plan.objects.get(category=cat, duration_weeks=24)
                    order_amt = plan.price
                
                active_client.us_revenue = (active_client.us_revenue or Decimal('0')) + Decimal(str(order_amt))
                coach_revenue_obj, _created = CoachRevenue.objects.get_or_create(coach=client_obj.coach)
                
                    
                coach_revenue_obj.us_revenue = (coach_revenue_obj.us_revenue or Decimal('0')) + Decimal(str(order_amt))
                coach_revenue_obj.save()
                active_client.active = True
                active_client.location = "international"
                active_client.save()
                #print(active_client)
            else:
                active_client = Clinet_Coach.objects.filter(client=client_obj,coach=client_obj.coach).latest('start_date')
                active_client.us_revenue = (active_client.us_revenue or Decimal('0')) + Decimal(str(order_amt))
                active_client.location = "international"
                active_client.save()
            finance = Finance_details.objects.filter(client=client_obj, location="international").order_by('-start_date').first()
            finance.amount_paid = (finance.amount_paid or Decimal('0')) + Decimal(str(order_amt))
            if client_obj.plan == 1:
                finance.end_date = timezone.now()
                send_test_message(f"New consultaion call: {client_obj.name} ({client_obj.email}), Coach: {client_obj.coach.name}, Amount: US $ {order_amt}")
                Notification.objects.create(
            
                    message=f"{client_obj.name} ({client_obj.email}) booked a consultation call. Coach: {client_obj.coach.name}, Amount: US $ {order_amt}",
                    
                )

            elif client_obj.plan == 2:
                finance.end_date = timezone.now() + timezone.timedelta(weeks=12)
                send_test_message(f"New 12 week plan: {client_obj.name} ({client_obj.email}), Coach: {client_obj.coach.name}, Amount: US $ {order_amt}")
                Notification.objects.create(
                    
                    message=f"{client_obj.name} ({client_obj.email}) purchased a 12 week plan. Coach: {client_obj.coach.name}, Amount: US $ {order_amt}",
                    
                )
            elif client_obj.plan == 3:
                finance.end_date = timezone.now() + timezone.timedelta(weeks=24)
                send_test_message(f"New 24 week plan: {client_obj.name} ({client_obj.email}), Coach: {client_obj.coach.name}, Amount: US $ {order_amt}")
                Notification.objects.create(
                    
                    message=f"{client_obj.name} ({client_obj.email}) purchased a 24 week plan. Coach: {client_obj.coach.name}, Amount: US $ {order_amt}",
                    
                )
            
            finance.save()
            client_obj.save()
            

            

 

        except razorpay.errors.SignatureVerificationError:
            razorpay_client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )
            

            return Response({"error": "Payment verification failed.", "flag": "False"}, status=status.HTTP_400_BAD_REQUEST)
 
        return Response({"message": "Payment verified successfully.", "flag": "True"}, status=status.HTTP_200_OK)



from django.conf import settings

class CBuyNowAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            name = request.data.get('name')
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            coach_id = request.data.get('coach')
            plan = int(request.data.get('plan'))  # 3 or 6
            residence = request.data.get('residence')
            print(coach_id, "coach id")
            coach = get_object_or_404(CoachProfile, pk=coach_id)

            if ClientDetails.objects.filter(email=email).exists():
                client = ClientDetails.objects.get(email=email)
                client.payment_mode="cashfree"
                client.plan=plan
                client.coach = coach    
                client.residence=residence
                client.payment_status="pending"
                client.save()
            
            else:
                client = ClientDetails.objects.create(
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    coach=coach,                 # REQUIRED FK
                    residence=residence,
                    payment_mode="cashfree", 
                            # fixed
                    plan=plan
                )

            print(client.phone_number, "testing before")         
            finace_details = Finance_details.objects.create(client=client, location="domestic")
            data = ClientDetailsSerializer(client).data
            return Response(data, status=status.HTTP_201_CREATED)

        except ValueError:
            return Response({"detail": "Invalid plan. Use 3 or 6."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)






from decimal import Decimal, InvalidOperation
import time
import requests



def cf_base_url():
    env = getattr(settings, "CASHFREE_ENV", "sandbox")
    return "https://api.cashfree.com/pg" if env.upper() == "PROD" else "https://sandbox.cashfree.com/pg"

def cf_headers():
    app_id = getattr(settings, "CASHFREE_APP_ID", None)
    secret_key = getattr(settings, "CASHFREE_SECRET_KEY", None)
    print(app_id, secret_key, "cashfree keys")

    if not app_id or not secret_key:
        raise ValueError("Cashfree keys are not configured on the server.")
    return {
        "x-client-id": app_id,
        "x-client-secret": secret_key,
        "x-api-version": "2023-08-01",
        "Content-Type": "application/json",
    }

class CPaymentInitializationView(APIView):
    """
    Creates a Cashfree Order for a given client (ClientDetails) and returns payment_session_id.
    Frontend should use Cashfree Drop/Checkout with this session.
    """
    permission_classes = [AllowAny]

    def post(self, request, client_id):
        try:
            client = get_object_or_404(ClientDetails, id=client_id)
            #print(getattr(settings, "CASHFREE_SECRET_KEY", None))
            # Block repeat payments
            #coach = get_object_or_404(CoachProfile, id=coach_id)
            if client.payment_status == "paid":
                return Response({"error": "Payment already completed for this client."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Pricing lookup (coach level + 'international' plan row to mirror your Razorpay logic)
                   # 'junior' | 'senior' | 'elite'
            coach_level = client.coach.coach_level        # 'junior' | 'senior' | 'elite'
            location = "domestic"
            cat = get_object_or_404(Category, coach_level=coach_level, location=location)

            # Amount (3 or 6 months)
            if client.plan == 1:
                plan = Plan.objects.get(category=cat,  duration_weeks=None)

                if not plan:
                    return Response({"error": "No plan found for the selected category and duration."}, status=status.HTTP_400_BAD_REQUEST)
                amount_dec = plan.price
            elif client.plan == 2:
                plan = Plan.objects.get(category=cat, duration_weeks=12)
                if Clinet_Coach.objects.filter(client=client, coach=client.coach).exists():
                    active_client = Clinet_Coach.objects.get(client=client, coach=client.coach)
                    active_client.duration_weeks = 12
                    active_client.save()
                else:
                    active_client = Clinet_Coach.objects.create(client=client, coach=client.coach, duration_weeks=12, active = False)
                if not plan:
                    return Response({"error": "No plan found for the selected category and duration."}, status=status.HTTP_400_BAD_REQUEST)
                plan = Plan.objects.get(category=cat, duration_weeks=12)
                amount_dec = plan.price
            elif client.plan == 3:
                plan = Plan.objects.get(category=cat, duration_weeks=24)
                if Clinet_Coach.objects.filter(client=client, coach=client.coach).exists():
                    active_client = Clinet_Coach.objects.get(client=client, coach=client.coach)
                    active_client.duration_weeks = 12
                    active_client.save()
                else:
                    active_client = Clinet_Coach.objects.create(client=client, coach=client.coach, duration_weeks=12, active = False)
                #if not 
                #    return Response({"error": "No plan found for the selected category and duration."}, status=status.HTTP_400_BAD_REQUEST)
                #
                amount_dec = plan.price
                
            else:
                return Response({"error": "Invalid plan.", "client_plan":client.plan}, status=status.HTTP_400_BAD_REQUEST)
            

            # Choose your currency (ensure it's enabled on your Cashfree account)
            #print(plan, amount_dec)
            order_currency = "INR"  # or "INR"
            order_amount = float(Decimal(amount_dec))  # Cashfree expects a float number
            print(client.phone_number)
            # Make a unique order_id for Cashfree (must be unique per order)
            order_id = f"client_{client.id}_{int(time.time())}"
            print(order_id, "order id")
            payload = {
                "order_id": order_id,
                "order_amount": order_amount,
                "order_currency": order_currency,
                "customer_details": {
                    "customer_id": str(client.id),
                    "customer_email": client.email or "noemail@example.com",
                    "customer_phone": (client.phone_number or "").strip()[:15],
                },
                # Optional: show success page and/or have Cashfree call this notify URL
                
                "order_note": f"Plan {client.plan} months | Coach: {coach_level} | Loc: {location}",
            }
            print(payload, "payload")   
            url = f"{cf_base_url()}/orders"
            headers = cf_headers()
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            print(resp.status_code, resp.text, "response")
            if resp.status_code not in (200, 201):
                return Response(
                    {"error": "Cashfree order creation failed", "status": resp.status_code, "response": resp.text},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = resp.json()
            payment_session_id = data.get("payment_session_id")
            if not payment_session_id:
                return Response({"error": "payment_session_id missing in Cashfree response", "response": data},
                                status=status.HTTP_400_BAD_REQUEST)

            # (Optional) Persist order_id/session if you want to map later
            # client.cashfree_order_id = order_id
            # client.save(update_fields=["cashfree_order_id"])

            app_id = getattr(settings, "CASHFREE_APP_ID", "")
            print(app_id, "app id")
            return Response({
                "cashfree_order_id": order_id,
                "payment_session_id": payment_session_id,
                "currency": order_currency,
                "amount": order_amount,
                "app_id": app_id,  # needed by Drop Checkout on the frontend
                "client": {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone_number": client.phone_number,
                    "plan": client.plan,
                    "coach_level": coach_level,
                    "location": location,
                }
            }, status=status.HTTP_200_OK)

        except (InvalidOperation, ValueError) as e:
            
            return Response({"error": "Amount computation failed", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Unexpected error", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CPaymentVerificationView(APIView):
    """
    Verifies Cashfree payment by fetching order status.
    Frontend should send `cashfree_order_id` after checkout completion.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        cashfree_order_id = request.data.get("cashfree_order_id")
        client_id = request.data.get("client_id")

        if not cashfree_order_id or not client_id:
            return Response({"error": "Missing cashfree_order_id or client_id."},
                            status=status.HTTP_400_BAD_REQUEST)

        client = get_object_or_404(ClientDetails, id=client_id)

        try:
            url = f"{cf_base_url()}/orders/{cashfree_order_id}"
            headers = cf_headers()
            resp = requests.get(url, headers=headers, timeout=30)

            if resp.status_code != 200:
                return Response(
                    {"error": "Failed to fetch order from Cashfree", "status": resp.status_code, "response": resp.text},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = resp.json()
            order_status = data.get("order_status")  # e.g., "PAID", "ACTIVE", "EXPIRED"
            cf_amount = data.get("order_amount")
            cf_currency = data.get("order_currency")

            if order_status == "PAID":
                client.payment_status = "paid"
                client.save(update_fields=["payment_status"])
                return Response({
                    "message": "Payment verified successfully.",
                    "flag": "True",
                    "order_status": order_status,
                    "amount": cf_amount,
                    "currency": cf_currency,
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "Payment not completed.",
                "flag": "False",
                "order_status": order_status,
                "amount": cf_amount,
                "currency": cf_currency,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Verification failed", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import json, hmac, hashlib, base64, time, logging
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ClientDetails

log = logging.getLogger("cashfree.webhook")

# --- simple idempotency cache (swap with Redis/DB in production) ---
_IDEMPOTENCY_SEEN = {}  # key -> ts

def _b64_hmac_sha256(secret: str, msg_bytes: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), msg_bytes, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

def _within_skew(ts_str: str, skew_sec: int = 10 * 60) -> bool:
    try:
        now = int(time.time())
        ts = int(ts_str)
        return abs(now - ts) <= skew_sec
    except Exception:
        return True  # if header missing or unparsable, don’t block during bring-up

@method_decorator(csrf_exempt, name="dispatch")
class CPaymentWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # --- 1) Basic header & secret checks ---
        secret = getattr(settings, "CASHFREE_WEBHOOK_SECRET", None)
        if not secret:
            log.error("Webhook secret not configured")
            return Response({"error": "secret not configured"}, status=500)

        raw = request.body or b""
        sig_hdr = request.headers.get("x-webhook-signature", "")
        ts_hdr = request.headers.get("x-webhook-timestamp", "")            # optional
        v_hdr  = request.headers.get("x-webhook-version", "")              # e.g., 2025-01-01
        idem   = request.headers.get("x-idempotency-key", "")              # base64 string

        if not sig_hdr:
            return Response({"error": "missing signature"}, status=400)

        # Optional: reject very old webhooks
        if ts_hdr and not _within_skew(ts_hdr):
            return Response({"error": "timestamp skew"}, status=400)

        # --- 2) Verify signature (Base64(HMAC_SHA256(body))) ---
        expected = _b64_hmac_sha256(secret, raw)
        if sig_hdr != expected:
            # Some accounts/extensions sign (timestamp + body). If yours does, uncomment:
            # alt = _b64_hmac_sha256(secret, (ts_hdr + raw.decode("utf-8", "ignore")).encode("utf-8"))
            # if sig_hdr != alt:
            log.warning("Signature mismatch (ver=%s)", v_hdr)
            return Response({"error": "invalid signature"}, status=400)

        # --- 3) Idempotency: drop duplicates ---
        if idem:
            if idem in _IDEMPOTENCY_SEEN:
                return Response({"status": "duplicate"}, status=200)
            _IDEMPOTENCY_SEEN[idem] = time.time()

        # --- 4) Parse body safely (keep raw text for HMAC) ---
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            return Response({"error": "bad json"}, status=400)

        event_type = payload.get("type")  # e.g., PAYMENT_SUCCESS_WEBHOOK, PAYMENT_FAILED_WEBHOOK, PAYMENT_USER_DROPPED_WEBHOOK
        data = payload.get("data") or {}
        order = data.get("order") or {}
        payment = data.get("payment") or {}
        customer = data.get("customer_details") or {}

        order_id = order.get("order_id")                   # ex: "order_OFR_2" or your custom one
        order_amt = order.get("order_amount")
        order_cur = order.get("order_currency")
        p_status = payment.get("payment_status")           # SUCCESS | FAILED | USER_DROPPED
        cf_payment_id = payment.get("cf_payment_id")
        p_msg = payment.get("payment_message")

        log.info("CF webhook v=%s type=%s order_id=%s p_status=%s cf_payment_id=%s",
                 v_hdr, event_type, order_id, p_status, cf_payment_id)

        # --- 5) Map your order_id back to a client (you were using client_<id>_...) ---
        client_obj = None
        client_id = None
        if order_id and order_id.startswith("client_"):
            parts = order_id.split("_")
            if len(parts) >= 2 and parts[1].isdigit():
                client_id = int(parts[1])
                client_obj = ClientDetails.objects.filter(id=client_id).first()

        # --- 6) Act on status ---
        if event_type == "PAYMENT_SUCCESS_WEBHOOK" or p_status == "SUCCESS":
            if client_obj and client_obj.payment_status != "paid":
                client_obj.payment_status = "paid"
                finance = Finance_details.objects.filter(client=client_obj, location="domestic").order_by('-date').first()
                finance.amount_paid += order_amt
                finance.save()
                client_obj.save(update_fields=["payment_status"])
                log.info("Client %s marked PAID (amount=%s %s)", client_id, order_amt, order_cur)
            return Response({"ok": True}, status=200)

        # Not paid cases (FAILED / USER_DROPPED). You can log or set a field if you track failures.
        if event_type in {"PAYMENT_FAILED_WEBHOOK", "PAYMENT_USER_DROPPED_WEBHOOK"} or p_status in {"FAILED", "USER_DROPPED"}:
            log.info("Payment not completed: %s (%s)", p_status, p_msg)
            # Optionally: persist last failure reason on the client/order model.
            finance = Finance_details.objects.filter(client=client_obj, location="domestic").order_by('-date').first()
            del finance
            return Response({"ok": True}, status=200)

        # Unknown event type—acknowledge to stop retries, but log for review.
        log.warning("Unhandled webhook type: %s", event_type)
        return Response({"ok": True}, status=200)


from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import hmac, hashlib, base64, json

secret = getattr(settings, "CASHFREE_WEBHOOK_SECRET", None)
CASHFREE_WEBHOOK_SECRET = "your_pg_secret_key"  # from PG Dashboard

def verify_signature(raw_body: bytes, signature_b64: str) -> bool:
    secret = getattr(settings, "CASHFREE_WEBHOOK_SECRET", None)
    if not secret:
        # Don’t 500 – just refuse verification cleanly
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature_b64 or "")

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import logging
from django.utils import timezone
log = logging.getLogger(__name__)


from .utils import send_test_message
@method_decorator(csrf_exempt, name="dispatch")
class CashfreeWebhookView(View):
    def post(self, request):
        raw = request.body
        sig = request.headers.get("x-webhook-signature")

        # Parse JSON
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        # Dashboard test pings sometimes include a simple marker
        data = payload.get("data") or {}
        if isinstance(data, dict) and data.get("test_object"):
            return JsonResponse({"message": "Test Webhook received"}, status=200)

        # Verify signature for real events BEFORE doing anything
        #if not sig or not verify_signature(raw, sig):
        #    return JsonResponse({"message": "Invalid signature"}, status=400)

        event_type = payload.get("type")  # e.g. PAYMENT_SUCCESS_WEBHOOK
        order = data.get("order") or {}
        payment = data.get("payment") or {}
        customer = data.get("customer_details") or {}

        order_id     = order.get("order_id")
        order_amt    = order.get("order_amount")
        order_cur    = order.get("order_currency")
        p_status     = (payment.get("payment_status") or "").upper()
        cf_payment_id= payment.get("cf_payment_id")
        p_msg        = payment.get("payment_message")

        # Map client id from order_id like "client_<id>_..."
        client_obj = None
        client_id = None
        if isinstance(order_id, str) and order_id.startswith("client_"):
            parts = order_id.split("_")
            if len(parts) >= 2 and parts[1].isdigit():
                client_id = int(parts[1])
                from admin_functions.models import ClientDetails  # adjust import path
                client_obj = ClientDetails.objects.filter(id=client_id).first()

        # Handle statuses
        if event_type == "PAYMENT_SUCCESS_WEBHOOK" or p_status == "SUCCESS":
            if client_obj and getattr(client_obj, "payment_status", None) != "paid":
                client_obj.payment_status = "paid"
                
                client_obj.save(update_fields=["payment_status"])
                client_obj.payment_date = timezone.now()
                if client_obj.plan != 1:
                    client_obj.active = True
                    active_client = Clinet_Coach.objects.get(client=client_obj,coach=client_obj.coach)
                    active_client.inr_revenue = (active_client.inr_revenue or Decimal('0')) + Decimal(str(order_amt))
                    coach_revenue_obj, _created = CoachRevenue.objects.get_or_create(coach=client_obj.coach)
                    
                        
                    coach_revenue_obj.inr_revenue = (coach_revenue_obj.inr_revenue or Decimal('0')) + Decimal(str(order_amt))
                    coach_revenue_obj.save()
                    active_client.active = True
                    active_client.location = "domestic"
                    active_client.save()
                    #print(active_client)
                else:
                    active_client = Clinet_Coach.objects.filter(client=client_obj,coach=client_obj.coach).latest('start_date')
                    active_client.inr_revenue = (active_client.inr_revenue or Decimal('0')) + Decimal(str(order_amt))
                    active_client.location = "domestic"
                    active_client.save()
                finance = Finance_details.objects.filter(client=client_obj, location="domestic").order_by('-start_date').first()
                finance.amount_paid = (finance.amount_paid or Decimal('0')) + Decimal(str(order_amt))
                if client_obj.plan == 1:
                    finance.end_date = timezone.now()
                    send_test_message(f"New consultaion call: {client_obj.name} ({client_obj.email}), Coach: {client_obj.coach.name}, Amount: INR {order_amt}")
                    Notification.objects.create(
                
                        message=f"{client_obj.name} ({client_obj.email}) booked a consultation call. Coach: {client_obj.coach.name}, Amount: INR {order_amt}",
                        
                    )

                elif client_obj.plan == 2:
                    finance.end_date = timezone.now() + timezone.timedelta(weeks=12)
                    send_test_message(f"New 12 week plan: {client_obj.name} ({client_obj.email}), Coach: {client_obj.coach.name}, Amount: INR {order_amt}")
                    Notification.objects.create(
                        
                        message=f"{client_obj.name} ({client_obj.email}) purchased a 12 week plan. Coach: {client_obj.coach.name}, Amount: INR {order_amt}",
                        
                    )
                elif client_obj.plan == 3:
                    finance.end_date = timezone.now() + timezone.timedelta(weeks=24)
                    send_test_message(f"New 24 week plan: {client_obj.name} ({client_obj.email}), Coach: {client_obj.coach.name}, Amount: INR {order_amt}")
                    Notification.objects.create(
                        
                        message=f"{client_obj.name} ({client_obj.email}) purchased a 24 week plan. Coach: {client_obj.coach.name}, Amount: INR {order_amt}",
                        
                    )
                
                finance.save()
                client_obj.save()
                log.info("Client %s marked PAID (amount=%s %s, cf_payment_id=%s)",
                         client_id, order_amt, order_cur, cf_payment_id)
            return JsonResponse({"ok": True}, status=200)

        if event_type in {"PAYMENT_FAILED_WEBHOOK", "PAYMENT_USER_DROPPED_WEBHOOK"} or p_status in {"FAILED", "USER_DROPPED"}:
            log.info("Payment not completed: status=%s msg=%s cf_payment_id=%s", p_status, p_msg, cf_payment_id)
            finance = Finance_details.objects.filter(client=client_obj, location="domestic").order_by('-date').first()
            active_client = Clinet_Coach.objects.get(client=client_obj,coach=client_obj.coach)
            if not active_client.inr_revenue or not active_client.us_revenue:
                del active_client
            
            del finance
            return JsonResponse({"ok": True}, status=200)

        log.warning("Unhandled webhook type: %s", event_type)
        return JsonResponse({"ok": True, "note": "Unhandled type"}, status=200)
    


from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignupSerializer,
    EmailTokenObtainPairSerializer,
    AdminOnlyTokenObtainPairSerializer,
)

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class AdminLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AdminOnlyTokenObtainPairSerializer


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    Optional: add to blacklist by sending refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token required"}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"detail": "invalid token"}, status=400)
        return Response({"detail": "logged out"}, status=205)
    



from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

class ClinetCoachTableViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that returns client-coach assignments for table view.
    Optional filters:
      - ?start_date=YYYY-MM-DD  (lower bound, inclusive)
      - ?end_date=YYYY-MM-DD    (upper bound, inclusive)
    """
    queryset = Clinet_Coach.objects.select_related("client", "coach").all()
    serializer_class = ClinetCoachTableSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        start_str = self.request.query_params.get("start_date")
        end_str = self.request.query_params.get("end_date")

        if start_str:
            start_dt = parse_date(start_str)
            if not start_dt:
                raise ValidationError({"start_date": "Use YYYY-MM-DD format."})
            qs = qs.filter(start_date__gte=start_dt)

        if end_str:
            end_dt = parse_date(end_str)
            if not end_dt:
                raise ValidationError({"end_date": "Use YYYY-MM-DD format."})
            qs = qs.filter(start_date__lte=end_dt)

        return qs



from django.core.mail import send_mail
import os

class TestEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            send_mail(
                subject="Test Email from TruFit",
                message="This is a test email sent from the TruFit backend.",
                from_email="abishek.129.203@gmail.com",  # Must be a verified email
                recipient_list=["abishek.129.203@gmail.com"],
                fail_silently=False,
            )
            return Response({"message": "Test email sent successfully."}, status=status.HTTP_200_OK )
        except Exception as e:
            #print("SMTP USER:", os.environ.get("SES_SMTP_USER"))
            print("SMTP PASS:", os.environ.get("AWS_SES_ACCESS_KEY_ID"))    
            #print("SMTP PASS LEN:", os.environ.get("SES_SMTP_PASS",""))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        


class ClientTableView(APIView):
    """
    API endpoint that returns all clients in a tabular format.
    """
    permission_classes = [AllowAny]

    def get(self, request, start_date=None, end_date=None):
        if start_date and end_date:
            try:
                start_dt = parse_date(start_date)
                end_dt = parse_date(end_date)
                if not start_dt or not end_dt:
                    raise ValueError
                client_table = ClientTableSerializer(
                    ClientDetails.objects.filter(active=True, payment_date__range=(start_dt, end_dt)).order_by('-payment_date'),
                    many=True
                ).data
            except ValueError:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        elif start_date:
            try:
                start_dt = parse_date(start_date)
                if not start_dt:
                    raise ValueError
                client_table = ClientTableSerializer(
                    ClientDetails.objects.filter(active=True, payment_date__gte=start_dt).order_by('-payment_date'),
                    many=True
                ).data
            except ValueError:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        elif end_date:
            try:
                end_dt = parse_date(end_date)
                if not end_dt:
                    raise ValueError
                client_table = ClientTableSerializer(
                    ClientDetails.objects.filter(active=True, payment_date__lte=end_dt).order_by('-payment_date'),
                    many=True
                ).data
            except ValueError:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            client_table = ClientTableSerializer( ClientDetails.objects.filter(active=True).order_by('-payment_date'), many=True).data

        return Response(client_table, status=status.HTTP_200_OK)
    




from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from .models import Clinet_Coach
from .serializers import CoachTableSerializer

class CoachClientListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CoachTableSerializer

    def get_queryset(self):
        coach_id = self.kwargs.get("coach_id")
        if coach_id is None:
            raise ValidationError({"coach_id": "coach_id path parameter is required."})

        qs = (Clinet_Coach.objects
              .filter(coach_id=coach_id)
              .select_related("coach", "client")
              .order_by("-start_date"))
        
        # Optional: support ?active=true/false
        active = self.request.query_params.get("active")
        if active is not None:
            if active.lower() not in ("true", "false"):
                raise ValidationError({"active": "Use true or false."})
            qs = qs.filter(active=(active.lower() == "true"))
        return qs
    
from django.db.models import Sum

class CoachRevenueView(APIView):
    """
    API endpoint to return total US and INR revenue for a given coach.
    """

    def get(self, request, coach_id):
        try:
            totals = Clinet_Coach.objects.filter(coach_id=coach_id).aggregate(
                total_us_revenue=Sum('us_revenue'),
                total_inr_revenue=Sum('inr_revenue')
            )
            return Response(totals, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from .models import Clinet_Coach
from .serializers import CoachTableSerializer

class CoachClientListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CoachTableSerializer

    def get_queryset(self):
        coach_id = self.kwargs.get("coach_id")
        if coach_id is None:
            raise ValidationError({"coach_id": "coach_id path parameter is required."})

        qs = (Clinet_Coach.objects
              .filter(coach_id=coach_id)
              .select_related("coach", "client")
              .order_by("-start_date"))
        
        # Optional: support ?active=true/false
        active = self.request.query_params.get("active")
        if active is not None:
            if active.lower() not in ("true", "false"):
                raise ValidationError({"active": "Use true or false."})
            qs = qs.filter(active=(active.lower() == "true"))
        return qs
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ForgotPasswordRequestSerializer, VerifyOTPSerializer

class ForgotPasswordRequestView(APIView):
    permission_classes = []  # AllowAny
    authentication_classes = []

    def post(self, request):
        """
        POST { "email": "user@example.com", "new_password": "NewStrongPass123" }
        """
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)

from .models import PasswordResetOTP
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
User = get_user_model()

class VerifyOTPView(APIView):
    permission_classes = []  # AllowAny
    authentication_classes = []

    def post(self, request):
        
        
        new_password = request.data.get("new_password")
        conform_password = request.data.get("confirm_password")
        otp = request.data.get("otp")
        if not new_password  or not conform_password or not otp:
            return Response({"detail": "new_password, confirm_password and otp are required."}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != conform_password:
            return Response({"detail": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)
        otp = request.data.get("otp")
        user = User.objects.get(email="abishek.reddy.020502@gmail.com")
        orginal_otp = PasswordResetOTP.objects.filter(user= user).order_by('-created_at').first()
        if not orginal_otp:
            return Response({"detail": "go to forgot password"}, status=status.HTTP_400_BAD_REQUEST)
        if otp != orginal_otp.otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        new_password_hashed = make_password(new_password)
        
        user.password = new_password_hashed
        user.save()
        orginal_otp.delete()  # Invalidate OTP after use
        #serializer = VerifyOTPSerializer(data=request.data)
        #serializer.is_valid(raise_exception=True)
        #data = serializer.save()
        return Response({"message":"password reset"},  status=status.HTTP_200_OK)
    


from django.utils.dateparse import parse_date
from .models import Clinet_Coach
from django.db.models import Sum


class TestGitView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        #total_revenue = CoachRevenue.objects.aggregate(total=Sum('inr_revenue'))['total'] or 0
        return Response({"message": "Git test successful!"}, status=status.HTTP_200_OK)
    


from datetime import datetime, date
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Finance_details
import logging

logger = logging.getLogger(__name__)

class NewSignupsDomesticView(APIView):
    """
    Returns:
      - total_active_users: domestic users active at a point date (current_date),
        or any time during a date window [start_date, end_date] if provided.
      - new_signups: domestic users whose start_date falls within the same point/date window.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            start_date_str = request.data.get("start_date")
            end_date_str = request.data.get("end_date")
            current_date_str = request.data.get("current_date")

            # Parse to date objects (not datetimes)
            def parse_d(d):
                return datetime.strptime(d, "%Y-%m-%d").date() if d else None

            start_date = parse_d(start_date_str)
            end_date = parse_d(end_date_str)
            current_date = parse_d(current_date_str)

            qs = Finance_details.objects.filter(location="domestic")

            # Point-in-time mode (current_date provided)
            if current_date:
                # Active at current_date
                active_filter = (
                    Q(start_date__lte=current_date) &
                    (Q(end_date__isnull=True) | Q(end_date__gte=current_date))
                )
                total_active_users = qs.filter(active_filter).count()

                # New signups up to current_date (cumulative) — matches your prior behavior
                # If you want only "signups ON that date", use start_date=current_date.
                new_signups = qs.filter(start_date__lte=current_date).count()

                return Response({
                    "total_active_users": total_active_users,
                    "new_signups": new_signups,
                }, status=status.HTTP_200_OK)

            # Window mode ([start_date, end_date])
            # If only one bound given, assume a 1-day window at that date.
            if start_date and not end_date:
                end_date = start_date
            if end_date and not start_date:
                start_date = end_date
            if not start_date and not end_date:
                # No dates provided: use today as point-in-time
                today = date.today()
                active_filter = (
                    Q(start_date__lte=today) &
                    (Q(end_date__isnull=True) | Q(end_date__gte=today))
                )
                total_active_users = qs.filter(active_filter).count()
                new_signups = qs.filter(start_date__lte=today).count()
                return Response({
                    "total_active_users": total_active_users,
                    "new_signups": new_signups,
                }, status=status.HTTP_200_OK)

            # Overlap logic for [start_date, end_date]
            overlap = (
                Q(start_date__lte=end_date) &
                (Q(end_date__isnull=True) | Q(end_date__gte=start_date))
            )
            total_active_users = qs.filter(overlap).count()

            # New signups within window (inclusive)
            new_signups = qs.filter(start_date__gte=start_date, start_date__lte=end_date).count()

            return Response({
                "total_active_users": total_active_users,
                "new_signups": new_signups,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in FinanceDomesticView: {str(e)}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class NewSignupsIntView(APIView):
    """
    Returns:
      - total_active_users: domestic users active at a point date (current_date),
        or any time during a date window [start_date, end_date] if provided.
      - new_signups: domestic users whose start_date falls within the same point/date window.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            start_date_str = request.data.get("start_date")
            end_date_str = request.data.get("end_date")
            current_date_str = request.data.get("current_date")

            # Parse to date objects (not datetimes)
            def parse_d(d):
                return datetime.strptime(d, "%Y-%m-%d").date() if d else None

            start_date = parse_d(start_date_str)
            end_date = parse_d(end_date_str)
            current_date = parse_d(current_date_str)

            qs = Finance_details.objects.filter(location="international")

            # Point-in-time mode (current_date provided)
            if current_date:
                # Active at current_date
                active_filter = (
                    Q(start_date__lte=current_date) 
                )
                total_active_users = qs.filter(active_filter).count()

                # New signups up to current_date (cumulative) — matches your prior behavior
                # If you want only "signups ON that date", use start_date=current_date.
                new_signups = qs.filter(start_date__lte=current_date).count()

                return Response({
                    "total_active_users": total_active_users,
                    "new_signups": new_signups,
                }, status=status.HTTP_200_OK)

            # Window mode ([start_date, end_date])
            # If only one bound given, assume a 1-day window at that date.
            if start_date and not end_date:
                end_date = start_date
            if end_date and not start_date:
                start_date = end_date
            if not start_date and not end_date:
                # No dates provided: use today as point-in-time
                today = date.today()
                active_filter = (
                    Q(start_date__lte=today) &
                    (Q(end_date__isnull=True) | Q(end_date__gte=today))
                )
                total_active_users = qs.filter(active_filter).count()
                new_signups = qs.filter(start_date__lte=today).count()
                return Response({
                    "total_active_users": total_active_users,
                    "new_signups": new_signups,
                }, status=status.HTTP_200_OK)

            # Overlap logic for [start_date, end_date]
            overlap = (
                Q(start_date__lte=end_date) &
                (Q(end_date__isnull=True) | Q(end_date__gte=start_date))
            )
            total_active_users = qs.filter(overlap).count()

            # New signups within window (inclusive)
            new_signups = qs.filter(start_date__gte=start_date, start_date__lte=end_date).count()

            return Response({
                "total_active_users": total_active_users,
                "new_signups": new_signups,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in InternationalView: {str(e)}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .models import Finance_details

from datetime import datetime, date
from decimal import Decimal
from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class FinanceAmountByLocationView(APIView):
    """
    POST body (all optional):
      - location: "domestic" | "international" | "all" (default: "domestic")
      - current_date: "YYYY-MM-DD"  # exact-date mode -> start_date == current_date
      - start_date: "YYYY-MM-DD"    # window start
      - end_date: "YYYY-MM-DD"      # window end

    Window behavior when one end missing:
      - only start_date -> [start_date, today]
      - only end_date   -> (-∞, end_date]
      - neither         -> active today
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            location = (request.data.get("location") or "domestic").lower().strip()
            start_date_str = request.data.get("start_date")
            end_date_str = request.data.get("end_date")
            current_date_str = request.data.get("current_date")

            def parse_date(s):
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None

            S = parse_date(start_date_str)
            E = parse_date(end_date_str)
            D = parse_date(current_date_str)

            base_qs = Finance_details.objects.all()

            # Location filter
            if location in {"domestic", "international"}:
                base_qs = base_qs.filter(location=location)
            elif location != "all":
                return Response(
                    {"detail": "location must be 'domestic', 'international', or 'all'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Date filtering
            if D:
                # Exact-date mode: ONLY start_date equals current_date
                base_qs = base_qs.filter(start_date=D)
                total = base_qs.aggregate(
                    total_amount_paid=Coalesce(
                        Sum("amount_paid"),
                        Value(Decimal("0.00")),
                        output_field=DecimalField(max_digits=18, decimal_places=2)
                    )
                )["total_amount_paid"] or Decimal("0.00")
                print(base_qs)
                return Response({"location": location, "total_amount_paid": str(total)}, status=status.HTTP_200_OK) 
               
            else:
                today = date.today()
                if S and E:
                    overlap = Q(start_date__gte=S, start_date__lte=E)  # or start_date__range=(S, E)
                elif S and not E:
                    overlap = Q(start_date__gte=S)
                elif E and not S:
                    overlap = Q(start_date__lte=E)   # use __lt=E for strictly before
                else:
                    overlap = Q(start_date__lte=today)

            qs = base_qs.filter(overlap)

            if location == "all":
                rows = (
                    qs.values("location")
                    .annotate(total_amount_paid=Coalesce(
                        Sum("amount_paid"),
                        Value(Decimal("0.00")),
                        output_field=DecimalField(max_digits=18, decimal_places=2)
                    ))
                    .order_by("location")
                )

                totals = []
                grand_total = Decimal("0.00")
                for r in rows:
                    amt = r["total_amount_paid"] or Decimal("0.00")
                    totals.append({"location": r["location"], "total_amount_paid": str(amt)})
                    grand_total += amt

                return Response({"totals": totals, "grand_total": str(grand_total)}, status=status.HTTP_200_OK)

            total = qs.aggregate(
                total_amount_paid=Coalesce(
                    Sum("amount_paid"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )["total_amount_paid"] or Decimal("0.00")

            return Response({"location": location, "total_amount_paid": str(total)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


from django.db.models import Sum, Count, Q, Value, DecimalField
from django.db.models.functions import Coalesce

from .models import CoachProfile
from .serializers import CoachSummarySerializer

from .serializers import CoachSummarySerializer  # update this too

from django.db.models import Count, Q
from rest_framework.generics import ListAPIView

from .serializers import CoachSummarySerializer

class CoachSummaryView(ListAPIView):
    serializer_class = CoachSummarySerializer

    def get_queryset(self):
        return (
            CoachProfile.objects
            .annotate(
                total_clients=Count('coach_clients_rel', distinct=True),
                active_clients_count=Count(
                    'coach_clients_rel',
                    filter=Q(coach_clients_rel__active=True),
                    distinct=True
                ),
            )
            .select_related("revenues")  # pulls CoachRevenue in one query
        )

from .models import Leads
from .serializers import LeadsSerializer


class LeadCaptureView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LeadsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LeadsListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LeadsSerializer
    queryset = Leads.objects.all().order_by('-created_at')


class CoachCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        count = CoachProfile.objects.all().exclude(status="hard").count()
        return Response({"coach_count": count}, status=status.HTTP_200_OK)
    




from rest_framework import viewsets, permissions, parsers
from .models import TestImage
from .serializers import TestImageSerializer

class TestImageViewSet(viewsets.ModelViewSet):
    
    queryset = TestImage.objects.all().order_by("-id")
    #print( queryset)
    serializer_class = TestImageSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)


class CoachCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        #print(request.data)
        serializer = CoachProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from django.http import JsonResponse
from .utils import send_test_message  # or wherever you place it

def test_socket_view(request):
    send_test_message("Ping from test view!")
    return JsonResponse({"status": "sent"})




class NotificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        flag = False
        if Notification.objects.filter(read=False).exists():
            flag = True
        
        return Response({"flag" : flag}, status=status.HTTP_201_CREATED)


class NotificationListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # this is triggered on GET
        Notification.objects.filter(read=False).update(read=True)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class NotificationEditView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)
        if not notification:
            return Response({"detail": "Notification not found."}, status=status.HTTP_400_BAD_REQUEST)
        notification.read = True
        notification.save()
        return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)

    def delete(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)
        if not notification:
            return Response({"detail": "Notification not found."}, status=status.HTTP_400_BAD_REQUEST)
        notification.delete()
        return Response({"detail": "Notification deleted."}, status=status.HTTP_200_OK)
    


from .models import ClientDetails
from .serializers import TopClientsSerializer

class TopClientsByPaymentMode(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        recent_clients_ind = ClientDetails.objects.filter(payment_mode="cashfree").order_by('-created_date')[:5]
        recent_clients_us = ClientDetails.objects.filter(payment_mode="razorpay").order_by('-created_date')[:5]
        serializer_ind = TopClientsSerializer(recent_clients_ind, many=True)
        serializer_us = TopClientsSerializer(recent_clients_us, many=True)
        return Response({
            "indian_clients": serializer_ind.data,
            "us_clients": serializer_us.data
        }, status=status.HTTP_200_OK)
    


class EnquiryFormView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        goal = request.data.get("goal")

        send_mail(
            message=f"New enquiry from {name}\nEmail: {email}\nPhone: {phone_number}\nGoal: {goal}",
            subject="New Enquiry Form Submission",
            recipient_list=["abishek.reddy.020502@gmail.com"],
            from_email="abishek.reddy.020502@gmail.com",
        
        )
        return Response({"detail": "Enquiry submitted."}, status=status.HTTP_201_CREATED)
    


from datetime import date, datetime
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ClientDetails, Clinet_Coach

class ClientCoachStatsView(APIView):
    """
    POST /metrics/client-stats/
    Body JSON:
    {
        "location": "domestic" | "international",
        "current_date": "YYYY-MM-DD",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    }
    """

    def _parse_date(self, s):
        if not s:
            return None
        if isinstance(s, (date, datetime)):
            return s.date() if isinstance(s, datetime) else s
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def post(self, request):
        # 1. Get body params
        location = request.data.get("location") or "domestic"
        current_date = self._parse_date(request.data.get("current_date"))
        start_date = self._parse_date(request.data.get("start_date"))
        end_date = self._parse_date(request.data.get("end_date"))

        # 2. Map location -> payment_mode
        payment_mode = "cashfree" if location == "domestic" else "razorpay"

        # 3. Single day case
        if current_date:
            new_signups = ClientDetails.objects.filter(
                payment_mode=payment_mode,
                payment_status="paid",
                payment_date=current_date,
            ).count()

            active_clients = Clinet_Coach.objects.filter(
                active=True, location=location
            ).count()

            return Response(
                {"new_signups": new_signups, "active_clients": active_clients},
                status=status.HTTP_200_OK,
            )

        # 4. Range case defaults
        if not start_date:
            start_date = date(2000, 1, 1)
        if not end_date:
            end_date = timezone.now().date()

        if start_date > end_date:
            return Response(
                {"detail": "start_date cannot be after end_date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5. Range queries
        new_signups = ClientDetails.objects.filter(
            payment_mode=payment_mode,
            created_date__date__gte=start_date,
            created_date__date__lte=end_date,
        ).count()

        active_clients = Clinet_Coach.objects.filter(
            location=location
        ).filter(
            Q(start_date__gte=start_date, end_date__lte=end_date)
            | Q(start_date__gte=start_date, start_date__lte=end_date, end_date__isnull=True)
        ).count()

        return Response(
            {"new_signups": new_signups, "active_clients": active_clients},
            status=status.HTTP_200_OK,
        )
    


# =============== Client's Apis ============== 
from rest_framework.decorators import api_view, permission_classes

from rest_framework import status
from rest_framework.pagination import PageNumberPagination

@api_view(["GET"])
@permission_classes([AllowAny])
def coach_profile_list(request):
    """
    GET /api/coaches/
    Returns all coach profiles
    """
    qs = CoachProfile.objects.filter(status='active').prefetch_related('certifications')
    serializer = CoachProfileSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def coach_profile_detail(request, pk: int):
    """
    GET /api/coaches/<pk>/
    """
    try:
        coach = (
            CoachProfile.objects.prefetch_related("certifications")
            .get(pk=pk)
        )
    except CoachProfile.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CoachProfileSerializer(coach, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)

from django.http import JsonResponse, Http404

@api_view(['GET'])
@permission_classes([AllowAny])
def testimonial_list(request):
    testimonials = Testimonial.objects.all().order_by('-created_at')
    serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
    return Response(serializer.data)


# Get a single testimonial by ID
@api_view(['GET'])
@permission_classes([AllowAny])
def testimonial_detail(request, pk):
    try:
        testimonial = Testimonial.objects.get(pk=pk)
    except Testimonial.DoesNotExist:
        raise Http404("Testimonial not found")

    serializer = TestimonialSerializer(testimonial, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)