from django.urls import path
from . import views

app_name = 'enquete'

urlpatterns = [

    path('', views.home, name='home'),
    
    # URLs para Área (Classes)
    path('areas/', views.AreaListView.as_view(), name='area_list'),
    path('areas/criar/', views.AreaCreateView.as_view(), name='area_criar'),
    path('areas/<slug:slug>/', views.AreaDetailView.as_view(), name='area_detail'),
    path('areas/editar/<slug:slug>/', views.AreaUpdateView.as_view(), name='area_editar'),
    path('areas/deletar/<slug:slug>/', views.AreaDeleteView.as_view(), name='area_delete'),

    # URLs para Enquete (Funções)
    path('enquetes/', views.enquete_list, name='enquete_list'),
    path('enquetes/criar/', views.enquete_create, name='enquete_criar'),
    path('enquetes/<int:pk>/', views.enquete_detail, name='enquete_detail'),
    path('enquetes/editar/<int:pk>/', views.enquete_edit, name='enquete_editar'),
    path('enquetes/deletar/<int:pk>/', views.enquete_delete, name='enquete_delete'),

    # URLs para Pergunta (Funções)
    path('enquetes/<int:enquete_id>/perguntas/', views.pergunta_list, name='pergunta_list'),
    path('perguntas/<int:pk>/', views.pergunta_detail, name='pergunta_detail'),
    path('perguntas/editar/<int:pk>/', views.pergunta_edit, name='pergunta_editar'),
    path('perguntas/deletar/<int:pk>/', views.pergunta_delete, name='pergunta_delete'),
    path('enquetes/<int:enquete_id>/perguntas/criar/', views.pergunta_create, name='pergunta_criar'),
    path('enquetes/<int:enquete_id>/responder/', views.responder_enquete, name='responder_enquete'),
    path('enquetes/<int:enquete_id>/processar_resposta/', views.processar_resposta, name='processar_resposta'),

    # URLs para Opcao (Funções)
    path('perguntas/<int:pergunta_id>/opcoes/criar/', views.opcao_create, name='opcao_criar'),
    path('opcoes/editar/<int:pk>/', views.opcao_edit, name='opcao_editar'),
    path('opcoes/deletar/<int:pk>/', views.opcao_delete, name='opcao_delete'),
]