from django.test import TestCase, override_settings
from model_bakery import baker

from games.models import Game
from games.utils import Direction


class DirectionTest(TestCase):
    def test_initialize(self):
        """Test the default initial values are as expected"""
        direction = Direction()
        self.assertEqual(direction.row, "")
        self.assertEqual(direction.col, "")

    @override_settings(CONNECT_FOUR_ROWS=6, CONNECT_FOUR_COLUMNS=7)
    def test_is_valid(self):
        with self.subTest(
            msg="confirm (0, 0) coordinate can be the start coin "
            "for a row, column and right diagonal but not left diagonal connect four"
        ):
            self.assertTrue(
                Game.DIRECTIONS[0].is_valid(0, 0), msg="row direction valid"
            )
            self.assertTrue(
                Game.DIRECTIONS[1].is_valid(0, 0), msg="column direction valid"
            )
            self.assertTrue(
                Game.DIRECTIONS[2].is_valid(0, 0), msg="right diagonal direction valid"
            )
            self.assertFalse(
                Game.DIRECTIONS[3].is_valid(0, 0), msg="left diagonal direction invalid"
            )

        with self.subTest(
            msg="confirm (5, 6) cannot be the start coin for any directional connect four"
        ):
            self.assertFalse(
                Game.DIRECTIONS[0].is_valid(5, 6), msg="row direction invalid"
            )
            self.assertFalse(
                Game.DIRECTIONS[1].is_valid(5, 6), msg="column direction invalid"
            )
            self.assertFalse(
                Game.DIRECTIONS[2].is_valid(5, 6),
                msg="right diagonal direction invalid",
            )
            self.assertFalse(
                Game.DIRECTIONS[3].is_valid(5, 6), msg="left diagonal direction invalid"
            )

        with self.subTest(
            msg="confirm (0, 6) coordinate can be the start coin "
            "for a column and left diagonal but not right diagonal or row connect four"
        ):
            self.assertFalse(
                Game.DIRECTIONS[0].is_valid(0, 6), msg="row direction invalid"
            )
            self.assertTrue(
                Game.DIRECTIONS[1].is_valid(0, 6), msg="column direction valid"
            )
            self.assertFalse(
                Game.DIRECTIONS[2].is_valid(0, 6),
                msg="right diagonal direction invalid",
            )
            self.assertTrue(
                Game.DIRECTIONS[3].is_valid(0, 6), msg="left diagonal direction invalid"
            )

    def test_next_coordinate(self):
        with self.subTest(msg="(0, 0) coordinate valid direction next values"):
            self.assertEqual(
                Game.DIRECTIONS[0].next_coordinate(0, 0, 1),
                (0, 1),
                msg="move by one along row",
            )
            self.assertEqual(
                Game.DIRECTIONS[1].next_coordinate(0, 0, 1),
                (1, 0),
                msg="move by one along column",
            )
            self.assertEqual(
                Game.DIRECTIONS[2].next_coordinate(0, 0, 1),
                (1, 1),
                msg="move by one along row and column",
            )

        with self.subTest(msg="confirm (0, 6) coordinate valid direction next values"):
            self.assertEqual(
                Game.DIRECTIONS[1].next_coordinate(0, 6, 1),
                (1, 6),
                msg="move by one along column",
            )
            self.assertEqual(
                Game.DIRECTIONS[3].next_coordinate(0, 6, 1),
                (1, 5),
                msg="move by one along column and back one along row",
            )

    def test_connect_four(self):
        player_1 = baker.make("User", first_name="test", last_name="player1")
        player_2 = baker.make("User", first_name="test", last_name="player2")
        coins = {
            (0, 0): player_1,
            (0, 2): player_2,
            (1, 2): player_2,
            (2, 2): player_2,
            (3, 2): player_2,
        }
        with self.subTest(msg="confirm (0, 0) has no connect four in any direction"):
            for direction in Game.DIRECTIONS:
                self.assertFalse(direction.connect_four((0, 0), coins))

        with self.subTest(msg="confirm (0, 2) has only connect four column direction"):
            self.assertFalse(Game.DIRECTIONS[0].connect_four((0, 2), coins))
            self.assertTrue(Game.DIRECTIONS[1].connect_four((0, 2), coins))
            self.assertFalse(Game.DIRECTIONS[2].connect_four((0, 2), coins))
            self.assertFalse(Game.DIRECTIONS[3].connect_four((0, 2), coins))
