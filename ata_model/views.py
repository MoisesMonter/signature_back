from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Ata
from .serializers import AtaSerializer
from ai_tratament.views import process_text
from drf_spectacular.utils import extend_schema
from django.utils import timezone

@extend_schema(
    tags=['Ata'],
    summary="Create a new Ata",
    description="Endpoint to create a new Ata with a selected SignatureList.",
    request=AtaSerializer,
    responses={201: AtaSerializer}
)
class AtaCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        if not data.get('title'):
            data['title'] = f"Modelo ATA {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        serializer = AtaSerializer(data=data)
        if serializer.is_valid():
            ata = serializer.save(user=request.user)
            process_text(request.user, ata)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
