from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_alimentos, name='listar_alimentos'),
    path('criar/', views.criar_alimento, name='criar_alimento'),
    path('editar/<int:id>/', views.atualizar_alimento,name='atualizar_alimento'),
    path('deletar/<int:id>/', views.deletar_alimento,name='deletar_alimento'),
]