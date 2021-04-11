from django.urls import path

from . import views

urlpatterns = [
    path('', views.GameListView.as_view(), name='game_list'),
    path('<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('<int:pk>/<int:column>/', views.GameCoinRedirectView.as_view(), name='game_coin'),
]
