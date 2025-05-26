from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from enquete.models import Area, Tecnologia, Enquete, Pergunta, Opcao, Aluno, Resposta, MultiplaEscolhaResposta, User
from .serializers import (
    AreaSerializer, TecnologiaSerializer, EnqueteSerializer, PerguntaSerializer,
    OpcaoSerializer, AlunoSerializer, RespostaSerializer, MultiplaEscolhaRespostaSerializer,
    UserSerializer
)
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db import transaction

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Apenas usuários autenticados podem ver os usuários

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated] # Apenas usuários autenticados podem interagir com alunos

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Aluno.objects.all()
        return Aluno.objects.filter(user=self.request.user) # Usuário só vê o próprio perfil de aluno

    def perform_create(self, serializer):
        # Garante que um aluno seja criado para o usuário logado
        if self.request.user.is_authenticated and not hasattr(self.request.user, 'aluno'):
            serializer.save(user=self.request.user)
        else:
            raise serializers.ValidationError("Este usuário já possui um perfil de aluno ou não está autenticado.")

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Permite leitura para não autenticados, escrita para autenticados

class TecnologiaViewSet(viewsets.ModelViewSet):
    queryset = Tecnologia.objects.all()
    serializer_class = TecnologiaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class EnqueteViewSet(viewsets.ModelViewSet):
    queryset = Enquete.objects.all()
    serializer_class = EnqueteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def responder(self, request, pk=None):
        enquete = self.get_object()
        perguntas = enquete.pergunta_set.filter(ativa=True).order_by('id')
        
        aluno = None
        if request.user.is_authenticated:
            try:
                aluno = request.user.aluno
            except Aluno.DoesNotExist:
                aluno = Aluno.objects.create(user=request.user, nome=request.user.username)
        
        respostas_data = request.data.get('respostas', [])
        
        if not respostas_data:
            return Response({"detail": "Nenhuma resposta fornecida."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for resposta_item in respostas_data:
                pergunta_id = resposta_item.get('pergunta_id')
                opcoes_selecionadas_ids = resposta_item.get('opcoes_ids') # Pode ser int para UE ou list de int para ME

                if not pergunta_id or not opcoes_selecionadas_ids:
                    return Response({"detail": "Dados de resposta incompletos para uma pergunta."}, status=status.HTTP_400_BAD_REQUEST)

                pergunta = get_object_or_404(Pergunta, id=pergunta_id, enquete=enquete)

                if pergunta.tipo == Pergunta.UNICA_ESCOLHA:
                    if not isinstance(opcoes_selecionadas_ids, int):
                        return Response({"detail": f"Resposta inválida para pergunta de única escolha ({pergunta.id}): opções_ids deve ser um inteiro."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    opcao = get_object_or_404(Opcao, id=opcoes_selecionadas_ids, pergunta=pergunta)
                    Resposta.objects.create(
                        aluno=aluno,
                        pergunta=pergunta,
                        opcao=opcao
                    )
                elif pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
                    if not isinstance(opcoes_selecionadas_ids, list):
                        return Response({"detail": f"Resposta inválida para pergunta de múltipla escolha ({pergunta.id}): opções_ids deve ser uma lista de inteiros."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    opcoes = Opcao.objects.filter(id__in=opcoes_selecionadas_ids, pergunta=pergunta)
                    if len(opcoes) != len(opcoes_selecionadas_ids):
                        return Response({"detail": f"Uma ou mais opções selecionadas para a pergunta {pergunta.id} são inválidas."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    multipla_resposta = MultiplaEscolhaResposta.objects.create(
                        aluno=aluno,
                        pergunta=pergunta
                    )
                    multipla_resposta.opcoes.set(opcoes)
                else:
                    return Response({"detail": f"Tipo de pergunta desconhecido ou inativo: {pergunta.texto}"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Respostas salvas com sucesso!"}, status=status.HTTP_201_CREATED)


class PerguntaViewSet(viewsets.ModelViewSet):
    queryset = Pergunta.objects.all()
    serializer_class = PerguntaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Opcional: Filtrar perguntas por enquete (se a URL for aninhada)
    def get_queryset(self):
        queryset = super().get_queryset()
        enquete_id = self.kwargs.get('enquete_id')
        if enquete_id:
            queryset = queryset.filter(enquete_id=enquete_id)
        return queryset

    # Opcional: Para criar uma pergunta dentro de uma enquete específica
    def perform_create(self, serializer):
        enquete_id = self.kwargs.get('enquete_id')
        if enquete_id:
            enquete = get_object_or_404(Enquete, id=enquete_id)
            serializer.save(enquete=enquete)
        else:
            serializer.save()

class OpcaoViewSet(viewsets.ModelViewSet):
    queryset = Opcao.objects.all()
    serializer_class = OpcaoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        pergunta_id = self.kwargs.get('pergunta_id')
        if pergunta_id:
            queryset = queryset.filter(pergunta_id=pergunta_id)
        return queryset
    
    def perform_create(self, serializer):
        pergunta_id = self.kwargs.get('pergunta_id')
        if pergunta_id:
            pergunta = get_object_or_404(Pergunta, id=pergunta_id)
            serializer.save(pergunta=pergunta)
        else:
            serializer.save()

class RespostaViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly para respostas para evitar manipulação direta
    queryset = Resposta.objects.all()
    serializer_class = RespostaSerializer
    permission_classes = [IsAuthenticated] # Apenas usuários autenticados podem ver as respostas

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Resposta.objects.all()
        return Resposta.objects.filter(aluno__user=self.request.user)

class MultiplaEscolhaRespostaViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly para respostas
    queryset = MultiplaEscolhaResposta.objects.all()
    serializer_class = MultiplaEscolhaRespostaSerializer
    permission_classes = [IsAuthenticated] # Apenas usuários autenticados podem ver as respostas

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MultiplaEscolhaResposta.objects.all()
        return MultiplaEscolhaResposta.objects.filter(aluno__user=self.request.user)