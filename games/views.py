from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from .forms import GameForm
from .models import Game


class GameListView(LoginRequiredMixin, generic.ListView):
    model = Game

    def get_queryset(self):
        return Game.objects.filter(
            Q(player_1=self.request.user) | Q(player_2=self.request.user)
        ).order_by("-status", "-created_date")


class GameCreateView(LoginRequiredMixin, generic.CreateView):
    model = Game
    form_class = GameForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class GamePlayerMixin(UserPassesTestMixin):
    def test_func(self):
        game = get_object_or_404(Game, pk=self.kwargs["pk"])
        return self.request.user in (game.player_1, game.player_2)


class GameDetailView(LoginRequiredMixin, GamePlayerMixin, generic.DetailView):
    model = Game


class GameCoinRedirectView(LoginRequiredMixin, GamePlayerMixin, generic.RedirectView):

    permanent = False
    pattern_name = "game_detail"

    def get_redirect_url(self, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs["pk"])
        column = kwargs.pop("column")
        game.create_coin(user=self.request.user, column=column)
        return super().get_redirect_url(*args, **kwargs)


class GameCheckRedirectView(LoginRequiredMixin, GamePlayerMixin, generic.View):
    def get(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs["pk"])
        return JsonResponse(
            {
                "is_users_turn": game.is_users_turn(request.user.id),
                "is_game_over": not game.is_pending,
            }
        )
