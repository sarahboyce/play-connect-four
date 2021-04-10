from django.test import TestCase, override_settings
from model_bakery import baker
from freezegun import freeze_time


class CoinTest(TestCase):
    @override_settings(CONNECT_FOUR_ROWS=6, CONNECT_FOUR_COLUMNS=7)
    def test_string_method(self):
        player = baker.make('User', first_name="test", last_name="player")
        coin = baker.make('games.Coin', player=player, row=1, column=3)
        self.assertEqual(
            coin.__str__(),
            "test player to (1, 3)"
        )


@freeze_time("2012-01-14")
@override_settings(CONNECT_FOUR_ROWS=6, CONNECT_FOUR_COLUMNS=7)
class GameTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_1 = baker.make('User', first_name="test", last_name="player1")
        cls.player_2 = baker.make('User', first_name="test", last_name="player2")
        cls.game = baker.make('games.Game', player_1=cls.player_1, player_2=cls.player_2)

    def test_string_method(self):
        self.assertEqual(
            self.game.__str__(),
            "14/01/2012 test player1 vs test player2: P1"
        )

    def test_available_columns(self):
        with self.subTest():
            self.assertListEqual(
                self.game.available_columns,
                [0, 1, 2, 3, 4, 5, 6],
                msg="all columns are available as no coins"
            )

        with self.subTest():
            for column in [0, 3, 4]:
                baker.make('games.Coin', game=self.game, player=self.player_1, row=5, column=column)
            self.assertListEqual(
                self.game.available_columns,
                [1, 2, 5, 6],
                msg="only some columns available"
            )

        with self.subTest():
            for column in [1, 2, 5, 6]:
                baker.make('games.Coin', game=self.game, player=self.player_1, row=5, column=column)
            self.assertListEqual(
                self.game.available_columns,
                [],
                msg="no columns available"
            )
