from django.template import Context, Template
from model_bakery import baker

from .test_views import ViewTestCase


class GameExtrasTemplateTagTest(ViewTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_1 = baker.make('User', username="test.player1")

    def setUp(self):
        super().setUp()
        self.request = self.factory.get('')
        self.request.user = self.user
        game = baker.make('games.Game', player_1=self.player_1, player_2=self.user)
        self.context = Context({'game': game, 'request': self.request})

    def test_game_opponent(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% game_opponent game %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly
        self.assertInHTML(
            'test.player1',
            rendered_template,
        )

    def test_game_coin(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% game_coin game %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly
        self.assertInHTML(
            'bg-warning',
            rendered_template,
        )

    def test_game_badge(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% game_badge game %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly
        self.assertInHTML(
            '<span class="badge badge-secondary"><i class="fas fa-spinner fa-pulse"></i> test.player1&#x27;s turn!</span>',
            rendered_template,
        )

    def test_is_users_turn(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% is_users_turn game as users_turn %}'
            '{% if users_turn %}Hello World{% endif %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly, not users turn
        self.assertHTMLNotEqual(
            'Hello World',
            rendered_template,
        )

    def test_is_valid_col(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% is_valid_col game 1 as valid_col %}'
            '{% if valid_col %}Hello World{% endif %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly
        self.assertInHTML(
            'Hello World',
            rendered_template,
        )

    def test_game_detail_title(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% game_detail_title game %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly
        self.assertInHTML(
            "<i class='fas fa-spinner fa-pulse'></i> test.player1's turn!",
            rendered_template,
        )
