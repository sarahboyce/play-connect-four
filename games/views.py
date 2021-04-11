from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views import generic
from django.conf import settings

from .models import Game


class GameListView(LoginRequiredMixin, generic.ListView):
    model = Game

    def get_queryset(self):
        return Game.objects.filter(
            Q(player_1=self.request.user) | Q(player_2=self.request.user)
        ).order_by('-status').select_related('player_1', 'player_2', 'winner')


class GameDetailView(LoginRequiredMixin, generic.DetailView):
    model = Game
