from django.urls import path

from . import views

urlpatterns = [
    path("", views.GameListView.as_view(), name="game_list"),
    path("create/", views.GameCreateView.as_view(), name="game_create"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game_detail"),
    path(
        "<int:pk>/<int:column>/", views.GameCoinRedirectView.as_view(), name="game_coin"
    ),
    path(
        "<int:pk>/check_turn/",
        views.GameCheckRedirectView.as_view(),
        name="game_check_turn",
    ),
]
