from django.test import TestCase, RequestFactory
from model_bakery import baker

from games.models import Game
from games.views import GameListView


class ViewTestCase(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = baker.make('User', first_name="test", last_name="user")


class GameListViewTest(ViewTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_1 = baker.make('User', first_name="test", last_name="player1")
        cls.player_2 = baker.make('User', first_name="test", last_name="player2")
        baker.make('games.Game', 3, player_1=cls.player_1, player_2=cls.player_2)

    def setUp(self):
        super().setUp()
        self.request = self.factory.get('')
        self.request.user = self.user

    def create_mix_games(self):
        g1 = baker.make('games.Game', player_1=self.player_1, player_2=self.user)
        g2 = baker.make('games.Game', player_1=self.user, player_2=self.player_2, status=Game.Status.DRAW)
        g3 = baker.make(
            'games.Game',
            player_1=self.player_1, player_2=self.user, status=Game.Status.COMPLETE, winner=self.user,
        )
        return [g1.id, g2.id, g3.id]

    def test_game_list_loads_no_games(self):
        response = GameListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200, msg="page loads")

    def test_game_list_loads_mix_of_games(self):
        self.create_mix_games()
        response = GameListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200, msg="page loads")

    def test_filtered_list_in_context_no_data(self):
        view = GameListView()
        view.setup(self.request)

        qs = view.get_queryset()
        self.assertQuerysetEqual(qs, Game.objects.none())

    def test_filtered_list_in_context_mix_data(self):
        id_list = self.create_mix_games()
        view = GameListView()
        view.setup(self.request)

        qs = view.get_queryset()
        self.assertListEqual(list(qs.values_list('id', flat=True)), id_list)
