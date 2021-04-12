from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.db.models import Max, F, IntegerField, Value
from django.db.models.functions import Cast, Coalesce
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .utils import Direction


class Game(models.Model):

    class Status(models.TextChoices):
        PLAYER_1 = "P1", _("Player 1's Turn")
        PLAYER_2 = "P2", _("Player 2's Turn")
        DRAW = "D", _("Draw")
        COMPLETE = "C", _("Complete")

    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLAYER_1)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)
    created_date = models.DateTimeField(auto_created=True)

    COLUMNS = [i for i in range(settings.CONNECT_FOUR_COLUMNS)]
    DIRECTIONS = [
        Direction(col="+"),
        Direction(row="+"),
        Direction(row="+", col="+"),
        Direction(row="+", col="-"),
    ]

    def __str__(self):
        return f"{self.created_date.strftime('%d/%m/%Y')} {self.player_1} vs {self.player_2}: {self.status}"

    def get_absolute_url(self):
        return reverse('game_detail', kwargs={'pk': self.pk})

    def opponent(self, user_id):
        return f"{self.player_2 if user_id == self.player_1_id else self.player_1}"

    def status_dict(self, user_id):
        if self.winner and self.winner_id == user_id:
            return {
                'icon': 'trophy',
                'inner_text': 'You won!',
                'badge_class': 'success'
            }
        if self.winner:
            return {
                'icon': 'window-close',
                'inner_text': 'You lost!',
                'badge_class': 'secondary'
            }
        if self.status == Game.Status.DRAW:
            return {
                'icon': 'window-close',
                'inner_text': 'You drew!',
                'badge_class': 'secondary'
            }
        if self.is_users_turn(user_id):
            return {
                'icon': 'play',
                'inner_text': 'Your turn!',
                'badge_class': 'primary'
            }
        return {
            'icon': 'spinner fa-pulse',
            'inner_text': f"{self.opponent(user_id)}'s turn!",
            'badge_class': 'secondary'
        }

    def html_detail_title(self, user_id):
        status_dict = self.status_dict(user_id)
        return format_html(
            '<i class="fas fa-{icon}"></i> {inner_text}',
            icon=status_dict['icon'],
            inner_text=status_dict['inner_text'],
        )

    def html_badge(self, user_id):
        return format_html(
            '<span class="badge badge-{badge_class}"><i class="fas fa-{icon}"></i> {inner_text}</span>',
            **self.status_dict(user_id)
        )

    @cached_property
    def available_columns(self):
        """Return the list of columns where a coin can enter,
        this is the columns where there isn't a coin in the last row"""
        return [
            column for column in self.COLUMNS
            if column not in self.coins.filter(row=settings.CONNECT_FOUR_ROWS - 1).values_list('column', flat=True)
        ]

    @cached_property
    def last_move(self):
        """Return the last coin that was played"""
        return self.coins.order_by('-created_date').first()

    @property
    def is_pending(self):
        """Check whether the game is not complete and pending the next player's move"""
        return self.status in {Game.Status.PLAYER_1, Game.Status.PLAYER_2}

    @cached_property
    def coin_dict(self):
        """Return a dict where the coin location is the key and player is the item"""
        return {
            (row, col): player
            for row, col, player in self.coins.order_by('row', 'column').values_list('row', 'column', 'player')
        }

    def get_player_colour(self, user_id):
        if user_id == self.player_1_id:
            return "red"
        if user_id == self.player_2_id:
            return "yellow"
        return "white"

    def get_player_coin_class(self, user_id):
        if self.get_player_colour(user_id) == "red":
            return "text-light bg-danger"
        return "bg-warning"

    @cached_property
    def current_player_colour(self):
        if self.status == Game.Status.PLAYER_1:
            return self.get_player_colour(self.player_1_id)
        if self.status == Game.Status.PLAYER_2:
            return self.get_player_colour(self.player_2_id)
        return "white"

    def is_users_turn(self, user_id):
        return (self.status == Game.Status.PLAYER_1 and user_id == self.player_1_id) or \
               (self.status == Game.Status.PLAYER_2 and user_id == self.player_2_id)

    @cached_property
    def board_dict(self):
        return {
            row: {
                col: self.get_player_colour(self.coin_dict.get((row, col), None))
                for col in range(settings.CONNECT_FOUR_COLUMNS)
            }
            for row in reversed(range(settings.CONNECT_FOUR_ROWS))
        }

    def calculate_status(self):
        """Checks the games coins to calculate the status.
            If the board is full, the game is a draw without a winner.
            If there are 4 coins in a line, then the game is complete with a winner.
            Otherwise, the game is in progress:
                the player who didn't play the last coin is next determines the status
                when no coins have been played, player_1 is next and determines the status
        """

        # check whether the board is empty
        if len(self.coin_dict) == 0:
            return {"status": Game.Status.PLAYER_1}

        # loop through the game's coins and check whether the coin is the first in a connect 4 sequence
        for coordinate, player_id in self.coin_dict.items():
            for direction in Game.DIRECTIONS:
                if direction.connect_four(coordinate, self.coin_dict):
                    return {"status": Game.Status.COMPLETE, "winner_id": player_id}

        # as no winner, check whether the board is full
        if len(self.coin_dict) == settings.CONNECT_FOUR_ROWS * settings.CONNECT_FOUR_COLUMNS:
            return {"status": Game.Status.DRAW}

        # the player who didn't play the last coin is next determines the status
        return {"status": Game.Status.PLAYER_2 if self.last_move.player == self.player_1 else Game.Status.PLAYER_1}

    def create_coin(self, user, column):
        """Providing the column and user are valid, a coin is created in the 'dropped' coin location.
        Then the game is updated with the new status and returns whether the game is complete"""

        if user not in {self.player_1, self.player_2}:
            raise ValueError("User is not part of the game")

        valid_status = {self.player_1: Game.Status.PLAYER_1, self.player_2: Game.Status.PLAYER_2}
        if valid_status[user] != self.status:
            raise ValueError(f"It is not {user}'s turn!")

        if column not in self.available_columns:
            raise ValueError("Column is filled!")

        row = self.coins.filter(
            column=column
        ).annotate(
            next_row=Cast(F('row') + 1, IntegerField())
        ).aggregate(
            col_next_row=Coalesce(Max('next_row'), Value(0))
        ).get('col_next_row', 0)

        Coin.objects.create(game=self, player=user, column=column, row=row)

        # recalculate the game status and save the result
        self.__dict__.update(self.calculate_status())
        self.save()

        # return whether the game is over
        return self.status in {Game.Status.COMPLETE, Game.Status.DRAW}


class Coin(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="coins")
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    column = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(settings.CONNECT_FOUR_COLUMNS - 1)]
    )
    row = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(settings.CONNECT_FOUR_ROWS - 1)]
    )
    created_date = models.DateTimeField(auto_now_add=True)

    unique_together = ['game', 'column', 'row']

    def __str__(self):
        return f"{self.player} to ({self.row}, {self.column})"
