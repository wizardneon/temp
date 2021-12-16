from typing import Any

from tortoise.models import Model
from tortoise import fields


class PlayerInGameModel(Model):
    game_model = fields.ManyToManyField('models.GameModel', related_name='player_in_game', through='player_with_game')
    player_id = fields.IntField()
    player_full_name = fields.TextField()
    player_even_time_on_ice = fields.TextField()

    def __init__(self, player_id, player_full_name, player_even_time_on_ice, **kwargs: Any):
        super().__init__(**kwargs)
        self.player_id = player_id
        self.player_full_name = player_full_name
        self.player_even_time_on_ice = player_even_time_on_ice
