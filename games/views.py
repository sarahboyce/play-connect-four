from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views import generic

from .models import Game


class GameListView(LoginRequiredMixin, generic.ListView):
    model = Game

    def get_queryset(self):
        return Game.objects.filter(
            Q(player_1=self.request.user) | Q(player_2=self.request.user)
        ).order_by('-status').select_related('player_1', 'player_2', 'winner')


class GameDetailView(LoginRequiredMixin, generic.DetailView):
    model = Game


class GameCoinRedirectView(LoginRequiredMixin, generic.RedirectView):

    permanent = False
    pattern_name = 'game_detail'

    def get_redirect_url(self, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        column = kwargs.pop('column')
        game.create_coin(user=self.request.user, column=column)
        return super().get_redirect_url(*args, **kwargs)

