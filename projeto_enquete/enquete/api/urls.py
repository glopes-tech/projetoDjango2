# enquete/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'areas', views.AreaViewSet)
router.register(r'tecnologias', views.TecnologiaViewSet)
router.register(r'enquetes', views.EnqueteViewSet)
router.register(r'perguntas', views.PerguntaViewSet)
router.register(r'opcoes', views.OpcaoViewSet)
router.register(r'alunos', views.AlunoViewSet)
router.register(r'respostas-unica-escolha', views.RespostaViewSet)
router.register(r'respostas-multipla-escolha', views.MultiplaEscolhaRespostaViewSet)
router.register(r'users', views.UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # Adicionar URLs aninhadas se desejar:
    # path('enquetes/<int:enquete_id>/perguntas/', views.PerguntaViewSet.as_view({'get': 'list', 'post': 'create'}), name='enquete-perguntas-list'),
    # path('perguntas/<int:pergunta_id>/opcoes/', views.OpcaoViewSet.as_view({'get': 'list', 'post': 'create'}), name='pergunta-opcoes-list'),
]