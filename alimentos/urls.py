from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Tela inicial
    path('', views.inicio, name='inicio'),

    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Rotas de Recuperação de Senha (Django Auth Views)
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # CRUD de alimentos
    path('alimentos/', views.listar_alimentos, name='listar_alimentos'),
    path('alimentos/criar/', views.criar_alimento, name='criar_alimento'),
    path('alimentos/editar/<int:id>/', views.atualizar_alimento, name='atualizar_alimento'),
    # Ver lotes do alimento
    path('alimentos/<int:id>/', views.detalhes_alimento, name='detalhes_alimento'),

    # Editar lotes
    path('lotes/editar/<int:id>/', views.editar_lote, name='editar_lote'),

    # Movimentação
    path('movimentacao/', views.movimentacao_estoque, name='movimentacao_estoque'),

    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/<str:tipo>/', views.relatorio_movimentacoes, name='relatorio_movimentacoes'),
    path('produtos-em-falta/', views.produtos_em_falta, name='produtos_em_falta'),
    path('relatorios/<str:tipo>/pdf/', views.exportar_pdf_movimentacoes, name='exportar_pdf_movimentacoes'),

    path('ativar/<uidb64>/<token>/', views.ativar_conta, name='ativar_conta'),

    # Aprovação e gerenciamento de contas (coordenadora/diretora)
    path('contas/aprovar/', views.aprovar_contas, name='aprovar_contas'),
    path('contas/aprovar/<int:id>/', views.aprovar_conta, name='aprovar_conta'),
    path('contas/recusar/<int:id>/', views.recusar_conta, name='recusar_conta'),
    path('contas/promover/<int:id>/', views.promover_admin, name='promover_admin'),
    path('contas/rebaixar/<int:id>/', views.rebaixar_admin, name='rebaixar_admin'),
    path('contas/excluir/<int:id>/', views.excluir_conta, name='excluir_conta'),
]