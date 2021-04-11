from django.template import Context, Template
from model_bakery import baker

from .test_views import ViewTestCase


class GameExtrasTemplateTagTest(ViewTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player_1 = baker.make('User', first_name="test", last_name="player1")
        cls.player_2 = baker.make('User', first_name="test", last_name="player2")

    def setUp(self):
        super().setUp()
        self.request = self.factory.get('')
        self.request.user = self.user
        game = baker.make('games.Game', player_1=self.player_1, player_2=self.user)
        self.context = Context({'game': game, 'request': self.request})

    def test_game_title(self):
        template_to_render = Template(
            '{% load game_extras %}'
            '{% game_title game %}'
        )
        rendered_template = template_to_render.render(self.context)
        # test that template tag loads correctly
        self.assertInHTML(
            '<span class="text-danger"><i class="fas fa-coins"></i></span> '
            'test player1 challenges <span class="text-warning"><i class="fas fa-coins"></i></span> you',
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
            '<span class="badge badge-primary"><i class="fas fa-play"></i> Continue</span>',
            rendered_template,
        )
