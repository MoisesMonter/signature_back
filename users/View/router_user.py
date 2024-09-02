from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer, LimitedUserSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()

@extend_schema_view(
    list=extend_schema(
        description="Lista de todos os usuários com dados limitados.",
        responses=LimitedUserSerializer
    ),
    retrieve=extend_schema(
        description="Retorna os dados limitados de qualquer usuário, incluindo o próprio.",
        responses={200: LimitedUserSerializer, 403: "Permissão Negada"}
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return LimitedUserSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            serializer = UserSerializer(user, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'photo_url' in data:
            data.pop('photo_url')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = LimitedUserSerializer(user)
        return Response(serializer.data)

    def get_queryset(self):
        return User.objects.all().only('id', 'first_name', 'email', 'photo_url')

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')