from itertools import cycle

from django.test import TestCase, override_settings
from freezegun import freeze_time
from model_bakery import baker

from games.models import Game


class CoinTest(TestCase):
    @override_settings(CONNECT_FOUR_ROWS=6, CONNECT_FOUR_COLUMNS=7)
    def test_string_method(self):
        player = baker.make("User", username="test.player")
        coin = baker.make("games.Coin", player=player, row=1, column=3)
        self.assertEqual(coin.__str__(), "test.player to (1, 3)")


@freeze_time("2012-01-14")
@override_settings(CONNECT_FOUR_ROWS=6, CONNECT_FOUR_COLUMNS=7)
class GameTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_1 = baker.make("User", username="test.player1")
        cls.player_2 = baker.make("User", username="test.player2")
        cls.game = baker.make(
            "games.Game", player_1=cls.player_1, player_2=cls.player_2
        )

    def test_string_method(self):
        self.assertEqual(
            self.game.__str__(), "14/01/2012 test.player1 vs test.player2: P1"
        )

    def test_get_absolute_url(self):
        self.assertEqual(f"/{self.game.pk}/", self.game.get_absolute_url())

    def test_opponent(self):
        self.assertEqual(self.game.opponent(self.player_1.id), "test.player2")
        self.assertEqual(self.game.opponent(self.player_2.id), "test.player1")

    def test_html_detail_title(self):
        with self.subTest(msg="user is player_1"):
            self.assertEqual(
                '<i class="fas fa-play"></i> Your turn!',
                self.game.html_detail_title(user_id=self.player_1.id),
            )
        with self.subTest(msg="user is player_2"):
            self.assertEqual(
                '<i class="fas fa-spinner fa-pulse"></i> test.player1&#x27;s turn!',
                self.game.html_detail_title(user_id=self.player_2.id),
            )
        with self.subTest(msg="player 1 is winner"):
            player_1_winner = baker.make(
                "games.Game",
                player_1=self.player_1,
                player_2=self.player_2,
                winner=self.player_1,
            )
            self.assertEqual(
                '<i class="fas fa-trophy"></i> You won!',
                player_1_winner.html_detail_title(user_id=self.player_1.id),
            )
        with self.subTest(msg="player 1 is winner, user is player 2"):
            self.assertEqual(
                '<i class="fas fa-window-close"></i> You lost!',
                player_1_winner.html_detail_title(user_id=self.player_2.id),
            )
        with self.subTest(msg="player 1 is winner"):
            drew = baker.make(
                "games.Game",
                player_1=self.player_1,
                player_2=self.player_2,
                status=Game.Status.DRAW,
            )
            self.assertEqual(
                '<i class="fas fa-window-close"></i> You drew!',
                drew.html_detail_title(user_id=self.player_1.id),
            )

    def test_status_dict(self):
        with self.subTest(msg="Game in progress"):
            self.assertDictEqual(
                {"icon": "play", "inner_text": "Your turn!", "badge_class": "primary"},
                self.game.status_dict(user_id=self.player_1.id),
            )
            self.assertEqual(
                {
                    "icon": "spinner fa-pulse",
                    "inner_text": "test.player1's turn!",
                    "badge_class": "secondary",
                },
                self.game.status_dict(user_id=self.player_2.id),
            )

        with self.subTest(msg="Game drew"):
            draw = baker.make(
                "games.Game",
                player_1=self.player_1,
                player_2=self.player_2,
                status=Game.Status.DRAW,
            )
            self.assertEqual(
                {
                    "icon": "window-close",
                    "inner_text": "You drew!",
                    "badge_class": "secondary",
                },
                draw.status_dict(user_id=self.player_1.id),
            )

        with self.subTest(msg="Game won"):
            won = baker.make(
                "games.Game",
                player_1=self.player_1,
                player_2=self.player_2,
                status=Game.Status.COMPLETE,
                winner=self.player_1,
            )
            self.assertEqual(
                {"icon": "trophy", "inner_text": "You won!", "badge_class": "success"},
                won.status_dict(user_id=self.player_1.id),
            )
            self.assertEqual(
                {
                    "icon": "window-close",
                    "inner_text": "You lost!",
                    "badge_class": "secondary",
                },
                won.status_dict(user_id=self.player_2.id),
            )

    def test_html_badge(self):
        with self.subTest(msg="Game in progress"):
            self.assertEqual(
                '<span class="badge badge-primary"><i class="fas fa-play"></i> Your turn!</span>',
                self.game.html_badge(user_id=self.player_1.id),
            )
            self.assertEqual(
                '<span class="badge badge-secondary"><i class="fas fa-spinner fa-pulse"></i> test.player1&#x27;s turn!</span>',
                self.game.html_badge(user_id=self.player_2.id),
            )

        with self.subTest(msg="Game drew"):
            draw = baker.make(
                "games.Game",
                player_1=self.player_1,
                player_2=self.player_2,
                status=Game.Status.DRAW,
            )
            self.assertEqual(
                '<span class="badge badge-secondary"><i class="fas fa-window-close"></i> You drew!</span>',
                draw.html_badge(user_id=self.player_1.id),
            )

        with self.subTest(msg="Game won"):
            won = baker.make(
                "games.Game",
                player_1=self.player_1,
                player_2=self.player_2,
                status=Game.Status.COMPLETE,
                winner=self.player_1,
            )
            self.assertEqual(
                '<span class="badge badge-success"><i class="fas fa-trophy"></i> You won!</span>',
                won.html_badge(user_id=self.player_1.id),
            )
            self.assertEqual(
                '<span class="badge badge-secondary"><i class="fas fa-window-close"></i> You lost!</span>',
                won.html_badge(user_id=self.player_2.id),
            )

    def test_available_columns(self):
        with self.subTest():
            self.assertListEqual(
                self.game.available_columns,
                [0, 1, 2, 3, 4, 5, 6],
                msg="all columns are available as no coins",
            )

        with self.subTest():
            del self.game.__dict__["available_columns"]
            for column in [0, 3, 4]:
                baker.make(
                    "games.Coin",
                    game=self.game,
                    player=self.player_1,
                    row=5,
                    column=column,
                )
            self.assertListEqual(
                self.game.available_columns,
                [1, 2, 5, 6],
                msg="only some columns available",
            )

        with self.subTest():
            del self.game.__dict__["available_columns"]
            for column in [1, 2, 5, 6]:
                baker.make(
                    "games.Coin",
                    game=self.game,
                    player=self.player_1,
                    row=5,
                    column=column,
                )
            self.assertListEqual(
                self.game.available_columns, [], msg="no columns available"
            )

    def test_last_move(self):
        with self.subTest(msg="no coins therefore last move is none"):
            self.assertIsNone(self.game.last_move)

        with freeze_time("2012-01-03"):
            del self.game.__dict__["last_move"]
            first_coin = baker.make("games.Coin", game=self.game)

        with self.subTest(msg="single coin therefore last move is that coin"):
            self.assertEqual(
                self.game.last_move,
                first_coin,
            )

        with self.subTest(
            msg="multiple coins therefore last move is coin with latest creation date"
        ):
            del self.game.__dict__["last_move"]
            latest_coin = baker.make("games.Coin", game=self.game)
            self.assertEqual(
                self.game.last_move,
                latest_coin,
            )

    def test_is_pending(self):
        with self.subTest(msg="game not pending when a draw"):
            draw_game = baker.make("games.Game", status=Game.Status.DRAW)
            self.assertFalse(draw_game.is_pending)
        with self.subTest(msg="game not pending when complete"):
            draw_game = baker.make("games.Game", status=Game.Status.COMPLETE)
            self.assertFalse(draw_game.is_pending)
        with self.subTest(msg="game pending when player 1s turn"):
            draw_game = baker.make("games.Game", status=Game.Status.PLAYER_1)
            self.assertTrue(draw_game.is_pending)
        with self.subTest(msg="game pending when player 2s turn"):
            draw_game = baker.make("games.Game", status=Game.Status.PLAYER_2)
            self.assertTrue(draw_game.is_pending)

    def test_coin_dict(self):
        # set up test coins
        baker.make("games.Coin", game=self.game, row=0, column=0, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=0, column=1, player=self.player_2)
        baker.make("games.Coin", game=self.game, row=1, column=1, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=2, column=2, player=self.player_2)
        self.assertDictEqual(
            self.game.coin_dict,
            {
                (0, 0): self.player_1.id,
                (0, 1): self.player_2.id,
                (1, 1): self.player_1.id,
                (2, 2): self.player_2.id,
            },
        )

    def test_get_player_colour(self):
        self.assertEqual(self.game.get_player_colour(self.player_1.id), "red")
        self.assertEqual(self.game.get_player_colour(self.player_2.id), "yellow")
        self.assertEqual(self.game.get_player_colour(0), "white")

    def test_get_player_coin_class(self):
        self.assertEqual(
            self.game.get_player_coin_class(self.player_1.id), "text-light bg-danger"
        )
        self.assertEqual(
            self.game.get_player_coin_class(self.player_2.id), "bg-warning"
        )

    def test_is_users_turn(self):
        self.assertTrue(
            self.game.is_users_turn(self.player_1.id), msg="True as player 1s turn"
        )
        self.assertFalse(
            self.game.is_users_turn(self.player_2.id), msg="False as player 1s turn"
        )

    def test_current_player_colour(self):
        with self.subTest(msg="Player 1 turn"):
            self.assertEqual(self.game.current_player_colour, "red")

        with self.subTest(msg="Player 2 turn"):
            player_2_game = baker.make(
                "games.Game",
                status=Game.Status.PLAYER_2,
                player_1=self.player_1,
                player_2=self.player_2,
            )
            self.assertEqual(player_2_game.current_player_colour, "yellow")

        with self.subTest(msg="No ones turn"):
            no_ones_game = baker.make(
                "games.Game",
                status=Game.Status.COMPLETE,
                player_1=self.player_1,
                player_2=self.player_2,
            )
            self.assertEqual(no_ones_game.current_player_colour, "white")

    def test_template_dict(self):
        # set up test coins
        baker.make("games.Coin", game=self.game, row=0, column=0, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=0, column=1, player=self.player_2)
        baker.make("games.Coin", game=self.game, row=1, column=1, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=2, column=2, player=self.player_2)
        self.assertDictEqual(
            self.game.board_dict,
            {
                0: {
                    0: "red",
                    1: "yellow",
                    2: "white",
                    3: "white",
                    4: "white",
                    5: "white",
                    6: "white",
                },
                1: {
                    0: "white",
                    1: "red",
                    2: "white",
                    3: "white",
                    4: "white",
                    5: "white",
                    6: "white",
                },
                2: {
                    0: "white",
                    1: "white",
                    2: "yellow",
                    3: "white",
                    4: "white",
                    5: "white",
                    6: "white",
                },
                3: {
                    0: "white",
                    1: "white",
                    2: "white",
                    3: "white",
                    4: "white",
                    5: "white",
                    6: "white",
                },
                4: {
                    0: "white",
                    1: "white",
                    2: "white",
                    3: "white",
                    4: "white",
                    5: "white",
                    6: "white",
                },
                5: {
                    0: "white",
                    1: "white",
                    2: "white",
                    3: "white",
                    4: "white",
                    5: "white",
                    6: "white",
                },
            },
        )

    def test_calculate_status_empty_board(self):
        """
        Empty Board:
        +---+---+---+---+---+---+
        | - | - | - | - | - | - |
        | - | - | - | - | - | - |
        | - | - | - | - | - | - |
        | - | - | - | - | - | - |
        | - | - | - | - | - | - |
        | - | - | - | - | - | - |
        | - | - | - | - | - | - |
        +---+---+---+---+---+---+
        """
        self.assertDictEqual(
            self.game.calculate_status(),
            {"status": Game.Status.PLAYER_1},
            msg="No coins in the board, therefore awaiting player 1's turn",
        )

    def test_calculate_status_full_board(self):
        """
        Filled board with coins but without a winner
        +----+----+----+----+----+----+
        | P2 | P1 | P2 | P1 | P2 | P1 |
        | P2 | P1 | P2 | P1 | P2 | P1 |
        | P1 | P2 | P1 | P2 | P1 | P2 |
        | P1 | P2 | P1 | P2 | P1 | P2 |
        | P2 | P1 | P2 | P1 | P2 | P1 |
        | P2 | P1 | P2 | P1 | P2 | P1 |
        | P1 | P2 | P1 | P2 | P1 | P2 |
        +----+----+----+----+----+----+
        """
        player_1_first = cycle([self.player_1, self.player_2])
        player_2_first = cycle([self.player_2, self.player_1])
        for row in range(2):
            for col in range(7):
                baker.make(
                    "games.Coin",
                    game=self.game,
                    row=row,
                    column=col,
                    player=player_1_first,
                )
        for row in range(2, 4):
            for col in range(7):
                baker.make(
                    "games.Coin",
                    game=self.game,
                    row=row,
                    column=col,
                    player=player_2_first,
                )
        for row in range(4, 6):
            for col in range(7):
                baker.make(
                    "games.Coin",
                    game=self.game,
                    row=row,
                    column=col,
                    player=player_1_first,
                )

        self.assertDictEqual(
            self.game.calculate_status(),
            {"status": Game.Status.DRAW},
            msg="The board is , therefore awaiting player 1's turn",
        )

    def test_calculate_status_player_1_won(self):
        """
        Player 1 wins the game
        +----+----+----+----+---+---+
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | P2 | P2 | P2 | -  | - |   |
        | P1 | P1 | P1 | P1 | - | - |
        +----+----+----+----+---+---+
        """
        baker.make("games.Coin", game=self.game, row=0, column=0, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=1, column=0, player=self.player_2)
        baker.make("games.Coin", game=self.game, row=0, column=1, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=1, column=1, player=self.player_2)
        baker.make("games.Coin", game=self.game, row=0, column=2, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=1, column=2, player=self.player_2)
        baker.make("games.Coin", game=self.game, row=0, column=3, player=self.player_1)

        self.assertDictEqual(
            self.game.calculate_status(),
            {"status": Game.Status.COMPLETE, "winner_id": self.player_1.id},
        )

    def test_calculate_status_player_2_turn(self):
        """
        No winner - Player 2's turn
        +----+----+----+----+---+---+
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | -  | -  | -  | - | - |
        | -  | P1 | -  | -  | - |   |
        | P1 | P2 | -  | -  | - | - |
        +----+----+----+----+---+---+
        """
        baker.make("games.Coin", game=self.game, row=0, column=0, player=self.player_1)
        baker.make("games.Coin", game=self.game, row=0, column=1, player=self.player_2)
        baker.make("games.Coin", game=self.game, row=1, column=1, player=self.player_1)

        self.assertDictEqual(
            self.game.calculate_status(), {"status": Game.Status.PLAYER_2}
        )

    def test_create_coin_user_not_payer(self):
        user = baker.make("User", first_name="stranger", last_name="danger")
        with self.assertRaisesMessage(ValueError, "User is not part of the game"):
            self.game.create_coin(user, 0)
        self.assertEqual(self.game.coins.count(), 0, msg="coin is not created")

    def test_create_coin_not_player_turn(self):
        with self.assertRaisesMessage(ValueError, "It is not test.player2's turn!"):
            self.game.create_coin(self.player_2, 0)
        self.assertEqual(self.game.coins.count(), 0, msg="coin is not created")

    def test_create_coin_col_invalid(self):
        baker.make("games.Coin", game=self.game, row=5, column=0)
        with self.assertRaisesMessage(ValueError, "Column is filled!"):
            self.game.create_coin(self.player_1, 0)
        self.assertEqual(self.game.coins.count(), 1, msg="second coin is not created")

    def test_create_coin_valid_first_row(self):
        self.assertFalse(
            self.game.create_coin(self.player_1, 0), msg="game is not complete"
        )

        self.game.refresh_from_db()
        coin = self.game.last_move
        # validate the coin is created as expected and game status updated
        self.assertEqual(coin.row, 0)
        self.assertEqual(coin.column, 0)
        self.assertEqual(coin.player, self.player_1)
        self.assertEqual(coin.game, self.game)
        self.assertEqual(self.game.status, Game.Status.PLAYER_2)

    def test_create_coin_valid_second_row(self):
        with freeze_time("2012-01-03"):
            baker.make(
                "games.Coin", game=self.game, row=0, column=0, player=self.player_2
            )

        self.assertFalse(
            self.game.create_coin(self.player_1, 0), msg="game is not complete"
        )

        self.game.refresh_from_db()
        coin = self.game.last_move
        # validate the coin is created as expected and game status updated
        self.assertEqual(coin.row, 1)
        self.assertEqual(coin.column, 0)
        self.assertEqual(coin.player, self.player_1)
        self.assertEqual(coin.game, self.game)
        self.assertEqual(self.game.status, Game.Status.PLAYER_2)
