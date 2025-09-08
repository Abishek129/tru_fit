from django.shortcuts import render

# Create your views here.

# admin_functions/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Blog, Testimonial, CoachProfile, CoachCertification, ClientDetails, Plans
from .serializers import BlogSerializer, TestimonialSerializer, CoachProfileSerializer, CoachCertificationSerializer, ClientDetailsSerializer, PlansSerializer, ClientDetailsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

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
    permission_classes = [permissions.AllowAny]

    # ✅ allow file uploads + JSON fields in the same request
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    # 🔎 searchable fields (removed non-existent bullet_points)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'coach_level', 'bio', 'tags', 'location', 'specializations']

    # ↕ ordering
    ordering_fields = ['id', 'name', 'experience', 'coach_level']


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


class PlansViewSet(viewsets.ModelViewSet):
    """
    CRUD for Blog with file upload support.
    """
    permission_classes = [AllowAny]
    queryset = Plans.objects.all()
    serializer_class = PlansSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]


class PriceAndPlans(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        location = request.data.get('location')
        category = request.data.get('category')
        plans = Plans.objects.get(location = location, category = category)
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
            if gender == "anyone":
                coaches = CoachProfile.objects.filter(~Q(coach_level="junior"))
            else:
                coaches = CoachProfile.objects.filter(~Q(coach_level="junior"), gender=gender)
                if not coaches:
                    coaches = CoachProfile.objects.filter(~Q(coach_level="junior"))

        else:
            if gender == "anyone":
                coaches = CoachProfile.objects.filter(coach_level="junior")
            else:
                coaches = CoachProfile.objects.filter(coach_level="junior", gender=gender)

        # Randomize order and select only 4 coaches
        coaches = coaches.order_by('?')[:4]

        serializer = CoachProfileSerializer(coaches, many=True)
        return Response(serializer.data)
    


from django.shortcuts import get_object_or_404

class RBuyNowAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            name = request.data.get('name')
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            coach_id = request.data.get('coach')
            plan = int(request.data.get('plan'))  # 3 or 6
            residence = request.data.get('residence')

            coach = get_object_or_404(CoachProfile, pk=coach_id)

            client = ClientDetails.objects.create(
                name=name,
                email=email,
                phone_number=phone_number,
                coach=coach,                 # REQUIRED FK
                residence=residence,
                payment_mode="razorpay",     # fixed
                plan=plan
            )

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

            # Block repeat payments
            if client.payment_status == "paid":
                return Response({"error": "Payment already completed for this client."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Pricing lookup (coach level + 'international' plan row)
            category = client.coach.coach_level        # 'junior' | 'senior' | 'elite'
            location = "international"
            plan_row = get_object_or_404(Plans, category=category, location=location)

            # Amount (3 or 6 months)
            if client.plan == 1:
                amount_dec = plan_row.consultation_call_price
            elif client.plan == 2:
                amount_dec = plan_row.short_term_price
            elif client.plan == 3:
                amount_dec = plan_row.long_term_price
            else:
                return Response({"error": "Invalid plan.", "client_plan":client.plan}, status=status.HTTP_400_BAD_REQUEST)
            
           

            # Razorpay client from env settings
            key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
            key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)
            if not key_id or not key_secret:
                return Response({"error": "Razorpay keys are not configured on the server."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            rz_client = razorpay.Client(auth=(key_id, key_secret))

            # USD: 2 decimal places → cents
            amount_minor = int((amount_dec * Decimal("100")).quantize(Decimal("1")))

            rz_order = rz_client.order.create({
                "amount": amount_minor,
                "currency": "USD",                     # USD-only
                "receipt": f"client_{client.id}",
                "payment_capture": 1,
                "notes": {
                    "client_id": str(client.id),
                    "client_email": client.email,
                    "plan_months": str(client.plan),
                    "coach_level": category,
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
                    "coach_level": category,
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
        client = get_object_or_404(ClientDetails, id=client_id)

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
            
            client.payment_status = "paid"
            
            

            client.save()

 

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

            coach = get_object_or_404(CoachProfile, pk=coach_id)

            client = ClientDetails.objects.create(
                name=name,
                email=email,
                phone_number=phone_number,
                coach=coach,                 # REQUIRED FK
                residence=residence,
                payment_mode="cashfree",     # fixed
                plan=plan
            )

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

    if not app_id or not secret_key:
        raise ValueError("Cashfree keys are not configured on the server.")
    return {
        "x-client-id": app_id,
        "x-client-secret": secret_key,
        "x-api-version": "2022-09-01",
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
            if client.payment_status == "paid":
                return Response({"error": "Payment already completed for this client."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Pricing lookup (coach level + 'international' plan row to mirror your Razorpay logic)
            category = client.coach.coach_level        # 'junior' | 'senior' | 'elite'
            location = "domestic"
            plan_row = get_object_or_404(Plans, category=category, location=location)

            # Amount (1, 3, or 6 months)
            if client.plan == 1:
                amount_dec = plan_row.consultation_call_price
            elif client.plan == 2:
                amount_dec = plan_row.short_term_price
            elif client.plan == 3:
                amount_dec = plan_row.long_term_price
            else:
                return Response({"error": "Invalid plan.", "client_plan": client.plan}, status=status.HTTP_400_BAD_REQUEST)

            # Choose your currency (ensure it's enabled on your Cashfree account)
            order_currency = "INR"  # or "INR"
            order_amount = float(Decimal(amount_dec))  # Cashfree expects a float number

            # Make a unique order_id for Cashfree (must be unique per order)
            order_id = f"client_{client.id}_{int(time.time())}"

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
                
                "order_note": f"Plan {client.plan} months | Coach: {category} | Loc: {location}",
            }

            url = f"{cf_base_url()}/orders"
            headers = cf_headers()
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
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
                    "coach_level": category,
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
                client_obj.save(update_fields=["payment_status"])
                log.info("Client %s marked PAID (amount=%s %s)", client_id, order_amt, order_cur)
            return Response({"ok": True}, status=200)

        # Not paid cases (FAILED / USER_DROPPED). You can log or set a field if you track failures.
        if event_type in {"PAYMENT_FAILED_WEBHOOK", "PAYMENT_USER_DROPPED_WEBHOOK"} or p_status in {"FAILED", "USER_DROPPED"}:
            log.info("Payment not completed: %s (%s)", p_status, p_msg)
            # Optionally: persist last failure reason on the client/order model.
            return Response({"ok": True}, status=200)

        # Unknown event type—acknowledge to stop retries, but log for review.
        log.warning("Unhandled webhook type: %s", event_type)
        return Response({"ok": True}, status=200)


@method_decorator(csrf_exempt, name="dispatch")
def cashfree_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("order_id")
        order_status = data.get("order_status")
        if order_id and order_id.startswith("client_"):
            parts = order_id.split("_")
            if len(parts) >= 2 and parts[1].isdigit():
                client_id = int(parts[1])
                client_obj = ClientDetails.objects.filter(id=client_id).first()
        

                client_obj.status = order_status
                client_obj.save()
            
                return JsonResponse({"message": "Webhook received"}, status=200)
        elif test_object in data:
            print("test webhook received")
            return JsonResponse({"message": "Test Webhook received"}, status=200)
        else :
            data = json.loads(request.body)
            order_id = data.get("order_id")
            order_status = data.get("order_status")
            print(data, order_id, order_status, )
            
            return JsonResponse({"message": "Webhook Failed"}, status=400)
    return JsonResponse({"detail": "Only POST"}, status=405)