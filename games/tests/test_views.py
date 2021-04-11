from django.test import TestCase, RequestFactory, override_settings
from model_bakery import baker

from games.models import Game, Coin
from games.views import GameListView, GameCoinRedirectView, GameCheckRedirectView


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


@override_settings(CONNECT_FOUR_ROWS=6, CONNECT_FOUR_COLUMNS=7)
class GameCoinRedirectViewTest(ViewTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_2 = baker.make('User', first_name="test", last_name="player2")

    def setUp(self):
        super().setUp()
        self.game = baker.make('games.Game', player_1=self.user, player_2=self.player_2)
        self.column = 1
        self.request = self.factory.get(f'/{self.game.pk}/{self.column}/')
        self.request.user = self.user

    def test_get_redirect_url(self):
        view = GameCoinRedirectView()
        view.setup(self.request)
        redirect_url = view.get_redirect_url(pk=self.game.pk, column=self.column)
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.Status.PLAYER_2, msg="Game updated to be next players turn")
        self.assertTrue(
            Coin.objects.filter(game=self.game, player=self.user, column=self.column, row=0).exists(),
            msg="Coin has been created as expected"
        )
        self.assertEqual(redirect_url, self.game.get_absolute_url(), msg="redirect to the game detail view")


class GameCheckRedirectViewTest(ViewTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_2 = baker.make('User', first_name="test", last_name="player2")

    def setUp(self):
        super().setUp()
        self.game = baker.make('games.Game', player_1=self.user, player_2=self.player_2)
        self.request = self.factory.get(f'/{self.game.pk}/check/')
        self.request.user = self.user

    def test_get_redirect_url(self):
        view = GameCheckRedirectView()
        view.setup(self.request)
        response = view.get(self.request, pk=self.game.pk)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'is_users_turn': True, 'is_game_over': False}
        )
