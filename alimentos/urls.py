from django.urls import path
from . import views

urlpatterns = [
    # Tela inicial
    path('', views.inicio, name='inicio'),

    # Autenticação
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # CRUD de alimentos
    path('alimentos/', views.listar_alimentos, name='listar_alimentos'),
    path('alimentos/criar/', views.criar_alimento, name='criar_alimento'),
    path('alimentos/editar/<int:id>/', views.atualizar_alimento, name='atualizar_alimento'),
    path('alimentos/deletar/<int:id>/', views.deletar_alimento, name='deletar_alimento'),

    # Movimentação
    path('movimentacao/', views.movimentacao, name='movimentacao'),

    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
]