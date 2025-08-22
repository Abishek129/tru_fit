from django.shortcuts import render

# Create your views here.

# admin_functions/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Blog, Testimonial, CoachProfile, CoachCertification, ClientDetails, Plans
from .serializers import BlogSerializer, TestimonialSerializer, CoachProfileSerializer, CoachCertificationSerializer, ClientDetailsSerializer, PlansSerializer
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

class RecommendCoachAPIView(APIView):
    def post(self, request):
        user_answers = request.data  # JSON from quiz
        coaches = recommend_coaches(user_answers, k=4)
        serializer = CoachProfileSerializer(coaches, many=True)
        return Response(serializer.data)

    



    
    
