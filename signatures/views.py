from PIL import Image
import base64
import io
import math

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from .models import SignatureList, Signature
from .serializers import SignatureListSerializer, SignatureSerializer,UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .serializers import PublicSignatureListSerializer, SignatureListSerializer
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

@extend_schema_view(
    list=extend_schema(
        tags=['Signature Lists'],
        description="Listar todas as listas de assinaturas de propriedade do usuário autenticado."
    ),
    retrieve=extend_schema(
        tags=['Signature Lists'],
        description="Recupere uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    create=extend_schema(
        tags=['Signature Lists'],
        description="Crie uma nova lista de assinaturas para o usuário autenticado."
    ),
    update=extend_schema(
        tags=['Signature Lists'],
        description="Atualizar uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    partial_update=extend_schema(
        tags=['Signature Lists'],
        description="Atualizar parcialmente uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    destroy=extend_schema(
        tags=['Signature Lists'],
        description="Excluir uma lista de assinaturas de propriedade do usuário autenticado."
    )
)
class SignatureListViewSet(viewsets.ModelViewSet):
    queryset = SignatureList.objects.all()
    serializer_class = SignatureListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        signature_list = self.get_object()

        if signature_list.owner == request.user:
            serializer = self.get_serializer(signature_list)
            return Response(serializer.data)
        else:
            return Response({"error": "Acesso negado. Apenas o proprietário pode acessar essa lista."}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        operation_id="Delete_Signature",
        summary="Delete uma assinatura específica de uma lista de assinaturas.",
        description="Deletes uma assinatura específica de uma lista de assinaturas de propriedade do usuário autenticado.",
        tags=['Signature Lists'],
        responses={
            204: "Signature deleted successfully.",
            403: {"error": "Acesso negado. Apenas o proprietário pode deletar essa assinatura."},
            404: {"error": "Assinatura ou lista não encontrada."},
        }
    )
    @action(detail=True, methods=['delete'], url_path='signature/(?P<signature_id>[^/.]+)')
    def delete_signature(self, request, pk=None, signature_id=None):
        signature_list = get_object_or_404(SignatureList, id=pk)

        if signature_list.owner != request.user:
            return Response({"error": "Acesso negado. Apenas o proprietário pode deletar essa assinatura."}, status=status.HTTP_403_FORBIDDEN)

        signature = get_object_or_404(Signature, id=signature_id, signature_list=signature_list)
        signature.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        operation_id="Update_SignatureList_State",
        summary="Atualizar o estado de uma lista de assinaturas e ajustar os sinalizadores das assinaturas.",
        description="Atualiza os campos `is_active` e `is_completed` de uma lista de assinaturas e ajusta os sinalizadores de assinaturas relacionadas.",
        tags=['Signature Lists'],
        request={
            'application/json': {
                'example': {
                    'is_active': True,
                    'is_completed': False
                }
            }
        },
        responses={
            200: OpenApiResponse(description="State updated and signatures flags adjusted successfully."),
            403: OpenApiResponse(description="Acesso negado. Apenas o proprietário pode alterar essa lista."),
            404: OpenApiResponse(description="Lista de assinaturas não encontrada."),
            500: OpenApiResponse(description="Erro interno do servidor."),
        },
    )
    @action(detail=True, methods=['patch'], url_path='update-state')
    def update_state(self, request, pk=None):
        try:
            # Obtém a lista de assinaturas garantindo que o usuário é o proprietário
            signature_list = get_object_or_404(SignatureList, pk=pk, owner=request.user)

            # Valida e atualiza os campos `is_active` e `is_completed`
            is_active = request.data.get('is_active')
            is_completed = request.data.get('is_completed')

            if is_active is not None and isinstance(is_active, bool):
                signature_list.is_active = is_active
            if is_completed is not None and isinstance(is_completed, bool):
                signature_list.is_completed = is_completed

            # Salva as mudanças na lista de assinaturas
            signature_list.save(update_fields=['is_active', 'is_completed'])

            # Atualiza as flags das assinaturas associadas ignorando as restrições de is_active
            for signature in signature_list.signatures.exclude(flag=3):
                if not signature_list.is_active and signature_list.is_completed:
                    signature.flag = 1  # Finalizado com sucesso
                elif not signature_list.is_active and not signature_list.is_completed:
                    signature.flag = 2  # Encerrado
                elif signature_list.is_active and not signature_list.is_completed:
                    signature.flag = 0  # Aberto
                else:
                    signature.flag = 0  # Valor padrão
                
                # Salva a assinatura permitindo operações em listas inativas
                signature.save(allow_inactive_operations=True)

            return Response({"message": "Estado atualizado e flags das assinaturas ajustadas com sucesso."}, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "Objeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Erro interno do servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        operation_id="Check_Password",
        summary="Verifica se uma lista de assinaturas requer senha.",
        description="Essa rota retorna um booleano indicando se a lista de assinaturas requer uma senha para acesso.",
        tags=['Signature Lists'],
        responses={
            200: OpenApiResponse(description="Indica se a lista de assinaturas requer uma senha.", examples=[
                {"requires_password": True},
                {"requires_password": False}
            ]),
            404: OpenApiResponse(description="Lista de assinaturas não encontrada."),
        },
    )
    @action(detail=True, methods=['get'], url_path='check-password', permission_classes=[AllowAny])
    def check_password(self, request, pk=None):
        try:
            signature_list = get_object_or_404(SignatureList, pk=pk)
            return Response({'requires_password': bool(signature_list.password)}, status=status.HTTP_200_OK)
        except SignatureList.DoesNotExist:
            return Response({"error": "Lista de assinaturas não encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        operation_id="Public_Signature_List_View",
        summary="Recupere uma lista de assinaturas sem assinaturas para qualquer usuário.",
        description="Este endpoint permite que qualquer usuário recupere os detalhes de uma lista de assinaturas sem expor as assinaturas. Ele retorna apenas as informações necessárias, como detalhes do proprietário, título, descrição, data de início, data de término e senha.",
        tags=['Signature Lists'],
        parameters=[
            OpenApiParameter(name='password', description='Password for the signature list, if required', required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(response=PublicSignatureListSerializer),
            403: OpenApiResponse(description="Senha incorreta."),
            404: OpenApiResponse(description="Lista de assinaturas não encontrada."),
        },
    )
    @action(detail=True, methods=['get'], url_path='public-view', permission_classes=[AllowAny])
    def public_view(self, request, pk=None):
        try:
            signature_list = get_object_or_404(SignatureList, pk=pk)
            input_password = request.query_params.get('password', '')  # Obtém a senha da query string
            if signature_list.password and signature_list.password != input_password:
                return Response({"error": "Senha incorreta."}, status=status.HTTP_403_FORBIDDEN)

            serializer = PublicSignatureListSerializer(signature_list)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SignatureList.DoesNotExist:
            return Response({"error": "Lista de assinaturas não encontrada."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        operation_id="Combine_Signatures_Images",
        summary="Combina assinaturas em uma única imagem.",
        description="Combina as assinaturas de uma lista de assinaturas em uma única imagem e a retorna.",
        tags=['Signature Lists'],
        responses={
            200: OpenApiResponse(description="Imagem combinada gerada com sucesso."),
            403: OpenApiResponse(description="Acesso negado. Apenas o proprietário pode acessar essa lista."),
            404: OpenApiResponse(description="Lista de assinaturas não encontrada."),
            500: OpenApiResponse(description="Erro ao gerar a imagem combinada."),
        },
    )
    @action(detail=True, methods=['get'], url_path='combine-signatures')
    def combine_signatures(self, request, pk=None):
        try:

            signature_list = get_object_or_404(SignatureList, pk=pk, owner=request.user)


            signatures = Signature.objects.filter(signature_list=signature_list).exclude(flag=3)
            base64_images = [signature.data for signature in signatures]


            images = [convert_base64_to_image(b64) for b64 in base64_images]*7
            

            combined_image = combine_images(images, columns=3)


            if not combined_image:
                return Response({"error": "Erro ao combinar imagens."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            buffered = io.BytesIO()
            combined_image = combined_image.convert("RGB")  
            combined_image.save(buffered, format="PNG")
            

            response = HttpResponse(buffered.getvalue(), content_type="image/png")
            response['Content-Disposition'] = 'attachment; filename="combined_signatures.png"'

            return response

        except Exception as e:
            print(f"Erro capturado: {str(e)}")
            return Response({"error": "Erro ao gerar a imagem combinada.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @extend_schema(
    #     operation_id="Combine_Signatures_Images",
    #     summary="Combina assinaturas em uma única imagem.",
    #     description="Combina as assinaturas de uma lista de assinaturas em uma única imagem e a retorna.",
    #     tags=['Signature Lists'],
    #     responses={
    #         200: OpenApiResponse(description="Imagem combinada gerada com sucesso."),
    #         403: OpenApiResponse(description="Acesso negado. Apenas o proprietário pode acessar essa lista."),
    #         404: OpenApiResponse(description="Lista de assinaturas não encontrada."),
    #         500: OpenApiResponse(description="Erro ao gerar a imagem combinada."),
    #     },
    # )
    # @action(detail=True, methods=['get'], url_path='combine-signatures')
    # def combine_signatures(self, request, pk=None):
    #     try:
 
    #         signature_list = get_object_or_404(SignatureList, pk=pk, owner=request.user)


    #         signatures = Signature.objects.filter(signature_list=signature_list).exclude(flag=3)
    #         base64_images = [signature.data for signature in signatures]

   
    #         images = [convert_base64_to_image(b64) for b64 in base64_images]
            

    #         combined_image = combine_images(images, columns=3)
            

    #         if not combined_image:
    #             return Response({"error": "Erro ao combinar imagens."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #         buffered = io.BytesIO()
    #         combined_image = combined_image.convert("RGB")  
    #         combined_image.save(buffered, format="PNG")


    #         return HttpResponse(buffered.getvalue(), content_type="image/png")

    #     except Exception as e:
    #         print(f"Erro capturado: {str(e)}")
    #         return Response({"error": "Erro ao gerar a imagem combinada.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # @extend_schema(
    #     operation_id="Combine_Signatures_Images",
    #     summary="Combina assinaturas em uma única imagem.",
    #     description="Combina as assinaturas de uma lista de assinaturas em uma única imagem e a retorna.",
    #     tags=['Signature Lists'],
    #     responses={
    #         200: OpenApiResponse(description="Imagem combinada gerada com sucesso."),
    #         403: OpenApiResponse(description="Acesso negado. Apenas o proprietário pode acessar essa lista."),
    #         404: OpenApiResponse(description="Lista de assinaturas não encontrada."),
    #         500: OpenApiResponse(description="Erro ao gerar a imagem combinada."),
    #     },
    # )
    # @action(detail=True, methods=['get'], url_path='combine-signatures')
    # def combine_signatures(self, request, pk=None):
    #     try:
    #         # Verifica se o usuário é o dono da lista de assinaturas
    #         print("Verificando o proprietário da lista...")
    #         signature_list = get_object_or_404(SignatureList, pk=pk, owner=request.user)
    #         print(f"Lista de Assinaturas encontrada: {signature_list}")

    #         # Busca todas as assinaturas da lista, excluindo aquelas com flag = 3
    #         print("Buscando assinaturas da lista...")
    #         signatures = Signature.objects.filter(signature_list=signature_list).exclude(flag=3)
    #         print(f"Assinaturas encontradas: {signatures}")
    #         base64_images = [signature.data for signature in signatures]

    #         # Exibindo a lista de base64 para verificação
    #         print("Lista de imagens em base64:", base64_images)
    #         new_base64_images = combined_image_to_base64(base64_images)
    #         # Retornando a lista para visualização no teste (apenas para fins de depuração)
    #         return Response({"base64_images": new_base64_images}, status=status.HTTP_200_OK)
          

    #     except Exception as e:
    #         print(f"Erro capturado: {str(e)}")
    #         return Response({"error": "Erro ao gerar a imagem combinada.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
        # try:
            # signature_list = get_object_or_404(SignatureList, pk=pk, owner=request.user)

        # Busca todas as assinaturas da lista, excluindo aquelas com flag = 3
            # signatures = Signature.objects.filter(signature_list=signature_list).exclude(flag=3)

            # Verifica se existem assinaturas na lista
            # if not signatures.exists():
            #     return Response({"error": "Nenhuma assinatura encontrada nesta lista."}, status=status.HTTP_404_NOT_FOUND)

            # Exemplo: Printando as assinaturas para verificação
            # for signature in signatures:
                # print(f"Assinatura ID: {signature.id}, Dados: {signature.data}")
            # Verifica se o usuário é o dono da lista de assinaturas
            # signature_list = get_object_or_404(SignatureList, pk=pk, owner=request.user)

            # Busca todas as assinaturas da lista, excluindo aquelas com flag = 3
            # signatures = Signature.objects.filter(signature_list=signature_list).exclude(flag=3)
            # print(signatures)
            # Verifica se existem assinaturas na lista
            # if not signatures.exists():
            #     return Response({"error": "Nenhuma assinatura encontrada nesta lista."}, status=status.HTTP_404_NOT_FOUND)

            # Converte cada assinatura (base64) para uma imagem PIL
            # images = []
            # for signature in signatures:
            #     base64_data = signature.data.split(",")[1]  # Extrai a parte base64 da string 'data:image/png;base64,...'
            #     image_data = base64.b64decode(base64_data)
            #     image = Image.open(io.BytesIO(image_data)).convert("RGBA")
            #     images.append(image)

            # Combina as imagens em uma única imagem
            # combined_image = self.combine_images(images)

            # Converte a imagem combinada para base64
            # buffered = io.BytesIO()
            # combined_image.save(buffered, format="PNG")
            # combined_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            # image_url = f"data:image/png;base64,{combined_base64}"

            # Retorna a imagem combinada como base64
            # return Response({"combined_image": signatures}, status=status.HTTP_200_OK)


    def combine_images(self, images, columns=4):
        """Combina uma lista de imagens PIL em uma única imagem."""
        if not images:
            raise ValueError("Nenhuma imagem fornecida para combinar.")

        # Redimensiona todas as imagens para o tamanho da primeira imagem
        img_width, img_height = images[0].size
        resized_images = [img.resize((img_width, img_height), Image.ANTIALIAS) for img in images]

        # Define o número de linhas baseado na quantidade de imagens e colunas
        rows = (len(resized_images) + columns - 1) // columns
        combined_image = Image.new('RGBA', (columns * img_width, rows * img_height), (255, 255, 255, 0))

        # Posiciona cada imagem na nova imagem combinada
        for index, image in enumerate(resized_images):
            x = (index % columns) * img_width
            y = (index // columns) * img_height
            combined_image.paste(image, (x, y))

        return combined_image

@extend_schema_view(
    list=extend_schema(
        tags=['Signatures'],
        description="Listar todas as assinaturas relacionadas às listas de assinaturas de propriedade do usuário autenticado."
    ),
    retrieve=extend_schema(
        tags=['Signatures'],
        description="Recupere uma assinatura específica relacionada a uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    create=extend_schema(
        tags=['Signatures'],
        description="Crie uma nova assinatura para uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    update=extend_schema(
        tags=['Signatures'],
        description="Atualizar uma assinatura relacionada a uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    partial_update=extend_schema(
        tags=['Signatures'],
        description="Atualizar parcialmente uma assinatura relacionada a uma lista de assinaturas de propriedade do usuário autenticado."
    ),
    destroy=extend_schema(
        tags=['Signatures'],
        description="Exclua uma assinatura relacionada a uma lista de assinaturas de propriedade do usuário autenticado."
    )
)
class SignatureViewSet(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer
    permission_classes = [IsAuthenticated]


    @extend_schema(
        operation_id="List_User_Participations",
        summary="Listar Listas de Assinaturas em que o Usuário Participou",
        description="Retorna todas as listas de assinaturas em que o usuário autenticado participou, incluindo apenas a assinatura específica do usuário.",
        responses={200: SignatureListSerializer(many=True)},
        tags=['Signatures']
    )
    @action(detail=False, methods=['get'], url_path='my_participations')
    def my_participations(self, request):

        
        signature_lists = SignatureList.objects.filter(signatures__user=request.user).distinct()


        results = []


        for signature_list in signature_lists:

            user_signature = signature_list.signatures.filter(user=request.user).first()


            owner_serialized = UserSerializer(signature_list.owner).data if signature_list.owner else {}

            
            results.append({
                "id": signature_list.id,
                "title": signature_list.title,
                "flag": user_signature.flag if user_signature else None,
                "created_at": signature_list.start_date, 
                "update_date": signature_list.update_date,
                "owner": owner_serialized, 
            })


        return Response(results, status=status.HTTP_200_OK)
    
    def perform_create(self, serializer):
        signature_list_id = self.request.data.get('signature_list')
        user = self.request.user

        # Verifica se já existe uma assinatura para esse usuário e lista
        existing_signature = Signature.objects.filter(signature_list_id=signature_list_id, user=user).first()

        if existing_signature:
            # Se a assinatura já existir, faz um PATCH para atualizar o estado
            serializer = self.get_serializer(existing_signature, data=self.request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Se não existir, cria uma nova assinatura
            serializer.save(user=user)

    def get_queryset(self):

        return self.queryset.filter(signature_list__owner=self.request.user)




def convert_base64_to_image(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    base64_string = base64_string + '=' * (-len(base64_string) % 4)
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    image.load()
    return image.convert("RGBA")  # Converte para RGBA para manter a transparência

def combine_images(images, columns=3):
    if not images:
        print("Nenhuma imagem fornecida para combinar.")
        return None
    if len(images)< columns:
        columns = len(images)
    rows = math.ceil(len(images) / columns)
    img_width, img_height = images[0].size
    combined_image = Image.new('RGBA', (columns * img_width, rows * img_height), (255, 255, 255, 0)) 

   
    for index, image in enumerate(images):
        x = (index % columns) * img_width
        y = (index // columns) * img_height
        combined_image.paste(image, (x, y), image) 

    return combined_image

def combined_image_to_base64(base64_images):
    images = [convert_base64_to_image(b64) for b64 in base64_images]
    combined_image = combine_images(images, columns=4)
    if combined_image:
        buffered = io.BytesIO()
        combined_image.save(buffered, format='PNG')
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    else:
        return None 