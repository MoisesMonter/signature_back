from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer

User = get_user_model()

class LoginAPI(APIView):
    permission_classes = []  # Permite o acesso sem autenticação

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['User Authentication'],  # Define a tag para a documentação
        description="Login ou registro de usuário sem senha."
    )
    def post(self, request):
        user_id = request.data.get("user_id", "").strip()
        first_name = request.data.get("first_name", "")
        email = request.data.get("email")
        photo_url = request.data.get("photo_url", "")

        if not email:
            return Response({"error": "Email é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if user_id:
                user = User.objects.get(user_id=user_id)
            else:
                user = User.objects.get(email=email)

            if first_name:
                user.first_name = first_name
            user.email = email
            if photo_url:
                user.photo_url = photo_url
            user.save()
            created = False
        except User.DoesNotExist:
            user = User.objects.create(
                user_id=user_id if user_id else None,
                first_name=first_name,
                email=email,
                username=user_id if user_id else email,
                photo_url=photo_url,
                is_active=True
            )
            created = True

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key
        })


from django.urls import path

urlpatterns = [
    path('login/', LoginAPI.as_view(), name='login'),  # Define a rota para login
]



    # def post(self, request):
    #     user = request.user  # Obtém o usuário autenticado a partir do token JWT

    #     if not user.is_authenticated:
    #         return Response({"error": "Usuário não autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

    #     # Obtém dados da requisição
    #     user_id = request.data.get("user_id", "")  # ID do usuário enviado pelo Clerk
    #     email = request.data.get("email", "")
    #     first_name = request.data.get("first_name", "")
    #     photo_url = request.data.get("photo_url", "")

    #     # Verifica se o usuário já existe pelo user_id do Clerk
    #     try:
    #         user = User.objects.get(username=user_id)
    #     except User.DoesNotExist:
    #         # Cria um novo usuário se ele não existir
    #         user = User.objects.create(
    #             username=user_id,  # Usa o ID do Clerk como username
    #             email=email,
    #             first_name=first_name,
    #             photo_url=photo_url,
    #             is_active=True
    #         )

    #     # Atualiza informações do usuário
    #     if first_name:
    #         user.first_name = first_name
    #     if email:
    #         user.email = email
    #     if photo_url:
    #         user.photo_url = photo_url
    #     user.save()

    #     # Extrai o token JWT do cabeçalho de autorização
    #     auth_header = request.headers.get('Authorization', '')
    #     token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

    #     # Retorna apenas o token JWT original
    #     return Response({"token": token}, status=status.HTTP_200_OK)