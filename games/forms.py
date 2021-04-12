from django.forms import ModelForm
from django_select2.forms import Select2Widget

from games.models import Game


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ("player_2",)
        widgets = {
            "player_2": Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.instance.player_1 = user
        player_2_qs = self.fields["player_2"].queryset.exclude(id=user.id)
        self.fields["player_2"].queryset = player_2_qs
