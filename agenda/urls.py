from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.teste, name='teste'),
    path('dashboard/', views.dashboard_salas, name='dashboard'),

    # Agendamentos
    path('novo/', views.novo_agendamento, name='novo_agendamento'),
    # path('meus/', views.meus_agendamentos, name='meus_agendamentos'),
    path('cancelar/<int:pk>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('admin/agendamentos/', views.todos_agendamentos, name='todos_agendamentos'),
    
    # Salas
    path('salas/', views.listar_salas, name='listar_salas'),
    path('salas/nova/', views.criar_sala, name='criar_sala'),
    path('salas/<int:pk>/editar/', views.editar_sala, name='editar_sala'),
    path('salas/<int:pk>/excluir/', views.excluir_sala, name='excluir_sala'),
    path('salas/<int:sala_id>/calendario/', views.calendario_sala, name='calendario_sala'),
    path('salas/<int:sala_id>/calendario/<int:ano>/<int:mes>/', views.calendario_sala, name='calendario_sala_mes'),
    path('salas/<int:sala_id>/dia/<str:data>/', views.detalhes_dia, name='detalhes_dia'),

]
