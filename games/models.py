from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.db.models import Max, F, IntegerField, Value
from django.db.models.functions import Cast, Coalesce
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

    DIRECTIONS = [
        Direction(col="+"),
        Direction(row="+"),
        Direction(row="+", col="+"),
        Direction(row="+", col="-"),
    ]

    def __str__(self):
        return f"{self.created_date.strftime('%d/%m/%Y')} {self.player_1.get_full_name()} vs {self.player_2.get_full_name()}: {self.status}"

    def html_title(self, user):
        is_player_1 = user == self.player_1
        is_player_2 = user == self.player_2
        player_1 = "You" if is_player_1 else self.player_1.get_full_name()
        player_2 = "you" if is_player_2 else self.player_2.get_full_name()

        return format_html(
            '<span class="text-danger"><i class="fas fa-coins"></i></span> {player_1} challenge{plural} '
            '<span class="text-warning"><i class="fas fa-coins"></i></span> {player_2}',
            player_1=player_1,
            plural="" if is_player_1 else "s",
            player_2=player_2,
        )

    def status_badge(self, user):
        badge_class = 'primary' if self.is_pending else 'secondary'
        icon = 'play'
        inner_text = 'Continue'
        if self.winner:
            icon = 'trophy'
            inner_text = f"{'You' if self.winner == user else self.winner.get_full_name()} Won"
        if self.status == Game.Status.DRAW:
            icon = 'sad-cry'
            inner_text = 'You Drew'
        span = f'<span class="badge badge-{badge_class}"><i class="fas fa-{icon}"></i> '
        return format_html(span + '{inner_text}</span>', inner_text=inner_text,)

    @property
    def available_columns(self):
        """Return the list of columns where a coin can enter,
        this is the columns where there isn't a coin in the last row"""
        return [
            i for i in range(settings.CONNECT_FOUR_COLUMNS)
            if i not in self.coins.filter(row=settings.CONNECT_FOUR_ROWS - 1).values_list('column', flat=True)
        ]

    @cached_property
    def last_move(self):
        """Return the last coin that was played"""
        return self.coins.order_by('-created_date').first()

    @property
    def is_pending(self):
        """Check whether the game is not complete and pending the next player's move"""
        return self.status in {Game.Status.PLAYER_1, Game.Status.PLAYER_2}

    def get_coin_dict(self):
        """Return a dict where the coin location is the key and player is the item"""
        return {
            (row, col): player
            for row, col, player in self.coins.order_by('row', 'column').values_list('row', 'column', 'player')
        }

    def calculate_status(self):
        """Checks the games coins to calculate the status.
            If the board is full, the game is a draw without a winner.
            If there are 4 coins in a line, then the game is complete with a winner.
            Otherwise, the game is in progress:
                the player who didn't play the last coin is next determines the status
                when no coins have been played, player_1 is next and determines the status
        """
        coins = self.get_coin_dict()

        # check whether the board is empty
        if len(coins) == 0:
            return {"status": Game.Status.PLAYER_1}

        # loop through the game's coins and check whether the coin is the first in a connect 4 sequence
        for coordinate, player in coins.items():
            for direction in Game.DIRECTIONS:
                if direction.connect_four(coordinate, coins):
                    return {"status": Game.Status.COMPLETE, "winner": player}

        # as no winner, check whether the board is full
        if len(coins) == settings.CONNECT_FOUR_ROWS * settings.CONNECT_FOUR_COLUMNS:
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
            raise ValueError(f"It is not {user.get_full_name()}'s turn!")

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
        return f"{self.player.get_full_name()} to ({self.row}, {self.column})"
