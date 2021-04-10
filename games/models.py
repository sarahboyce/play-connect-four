from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.db.models import Max, F, IntegerField
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _


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
        Direction(row="-", col="+"),
    ]

    def __str__(self):
        return f"{self.created_date.strftime('%d/%m/%Y')} {self.player_1.get_full_name()} vs {self.player_2.get_full_name()}: {self.status}"


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
