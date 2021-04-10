from django.contrib import admin
from . import models


class GameAdmin(admin.ModelAdmin):
    list_display = ('player_1', 'player_2', 'status', 'winner', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ['status', 'winner']


class CoinAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'column', 'row', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ['game', 'player']


admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Coin, CoinAdmin)
