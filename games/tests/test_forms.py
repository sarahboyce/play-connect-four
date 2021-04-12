from django.test import TestCase
from model_bakery import baker

from games.forms import GameForm


class GameFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_1 = baker.make("User", username="test.player1")
        cls.player_2 = baker.make("User", username="test.player2")

    def test_form_init(self):
        form = GameForm(user=self.player_1)
        with self.subTest(msg="check initialised with user as player_1"):
            self.assertEqual(
                form.instance.player_1,
                self.player_1,
            )
        with self.subTest(msg="check that cannot assign youself as opponent"):
            form.data["player_2"] = self.player_1.id
            self.assertFalse(form.is_valid())
