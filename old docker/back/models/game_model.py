from typing import Any

from tortoise.models import Model
from tortoise import fields


class GameModel(Model):
    game_pk = fields.IntField()
    date = fields.TextField()
    city = fields.TextField()
    home_team_name = fields.TextField()
    away_team_name = fields.TextField()
    goals_home = fields.IntField()
    goals_away = fields.IntField()

    def __init__(self, game_pk, date, city, home_team_name, away_team_name, goals_home, goals_away, **kwargs: Any):
        super().__init__(**kwargs)
        self.game_pk = game_pk
        self.date = date
        self.city = city
        self.home_team_name = home_team_name
        self.away_team_name = away_team_name
        self.goals_home = goals_home
        self.goals_away = goals_away
