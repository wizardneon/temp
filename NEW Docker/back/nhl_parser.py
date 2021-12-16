from tortoise import Tortoise
from tortoise.query_utils import Q

from models.player_in_game_model import PlayerInGameModel
from models.game_model import GameModel
from dateutil import parser

import json
import requests


class NhlParser:
    session = requests.Session()

    async def init(self, db_url):
        # статичные модули (питоновские файлы с моделями) в папке models
        models = ["models.game_model", "models.player_in_game_model"]
        # ранняя проверка связей между моделями
        Tortoise.init_models(models, "models")
        # установление подключения
        await Tortoise.init(
            db_url=db_url,
            modules={'models': models}
        )
        # создает таблички в случае, если они не существуют
        await Tortoise.generate_schemas()
        print('подключение к бд установлено, можно работать')

    async def parse_teams(self):
        # получение всех команд
        print('начато получение всех команд')
        url = 'https://statsapi.web.nhl.com/api/v1/teams'
        response = self.session.get(url=url)
        json_text = json.loads(response.text)

        teams = []
        json_teams = json_text['teams']

        for json_team in json_teams:
            teams.append(json_team['id'])

        print(f'все команды получены. всего {len(teams)} штук')
        return teams

    async def parse_games_for_teams(self, teams, start_date, end_date):
        # парсим игры от команд
        games_for_teams = []
        print(f'начато получение всех игр для всех команд в период с {start_date} по {end_date}. Это может занять '
              f'много времени')

        for team in teams:
            games = await self.parse_games_for_team(str(team), start_date, end_date)
            games_for_teams.extend(games)

        # уберем не уникальные значения
        games_for_teams = list(set(games_for_teams))
        print(f'все игры для каждой из команд получены. всего {len(games_for_teams)} уникальных игр за заданный период')
        return games_for_teams

    async def parse_games_for_team(self, team_id, start_date, end_date):
        url = 'https://statsapi.web.nhl.com/api/v1/schedule?teamId=' + \
              team_id + f'&startDate={start_date}&endDate={end_date}'
        games_for_teams = []
        response = self.session.get(url=url)
        try:
            json_games_for_teams = json.loads(response.text)

            for date in json_games_for_teams['dates']:
                for game in date['games']:
                    games_for_teams.append(game['gamePk'])
        except Exception as ex:
            print('ошибка: ', ex)

        print(f'сбор игр по команде id={team_id} в период с {start_date} по {end_date} завершен. '
              f'собрано игр: {len(games_for_teams)}')
        return games_for_teams

    async def parse_game_data_and_save(self, game_pk):
        # парсинг данных для каждой игры
        if await GameModel.exists(game_pk=str(game_pk)):
            # в базу данных не нужно класть эту игру, так как она уже там есть
            print(f'в базе уже есть игра с ключом = {game_pk}, пропускаем')
            return

        url = f'https://statsapi.web.nhl.com/api/v1/game/{game_pk}/feed/live'
        response = self.session.get(url=url)
        json_text = json.loads(response.text)

        # парсим остальные значения
        game_data = json_text['gameData']
        live_data = json_text['liveData']
        game_data_teams = game_data['teams']
        live_data_teams = live_data['boxscore']['teams']

        date_time = str(parser.parse(game_data['datetime']['dateTime']).date())
        city = game_data_teams['home']['locationName']
        home_team_name = game_data_teams['home']['name']
        away_team_name = game_data_teams['away']['name']
        goals_home = live_data_teams['home']['teamStats']['teamSkaterStats']['goals']
        goals_away = live_data_teams['away']['teamStats']['teamSkaterStats']['goals']

        # получаем модель игры и сохраняем ее
        game_model = GameModel(game_pk, date_time, city, home_team_name, away_team_name, goals_home, goals_away)
        await game_model.save()
        print(f'сохранили игру {game_pk}')

        # собираем всех игроков
        players = []
        json_players = json_text['liveData']['boxscore']['teams']['home']['players']
        for player in json_players.values():
            players.append(player)

        json_players = json_text['liveData']['boxscore']['teams']['away']['players']
        for player in json_players.values():
            players.append(player)

        # преобразуем их в модели игроков в игре и сохраняем их
        for player in players:
            person = player['person']
            player_id = person['id']

            player_full_name = ''
            if 'fullName' in person:
                # непонятно почему, но у некоторых людей карточки пусты
                player_full_name = person['fullName']

            player_even_time_on_ice = ''
            if 'skaterStats' in player['stats']:
                player_even_time_on_ice = player['stats']['skaterStats']['timeOnIce']
            elif 'goalieStats' in player['stats']:
                player_even_time_on_ice = player['stats']['goalieStats']['timeOnIce']

            player_in_game = PlayerInGameModel(player_id, player_full_name, player_even_time_on_ice)
            await player_in_game.save()
            await player_in_game.game_model.add(game_model)

    async def get_data(self, start_date, end_date):
        games = await GameModel.filter(Q(date__range=(start_date, end_date), join_type='AND'))\
            .prefetch_related('player_in_game')

        # полученные данные преобразуем в json
        games_json = list()
        for game in games:
            game_json = {
                'game_pk': game.game_pk,
                'date': game.date,
                'city': game.city,
                'home_team_name': game.home_team_name,
                'away_team_name': game.away_team_name,
                'goals_home': game.goals_home,
                'goals_away': game.goals_away,
                'player_in_game': [],
            }
            for pl in game.player_in_game:
                # игроков в статистике игры может и не быть, это не баг, так их апи устроено
                game_json['player_in_game'].append({
                    'player_id': pl.player_id,
                    'player_full_name': pl.player_full_name,
                    'player_even_time_on_ice': pl.player_even_time_on_ice,
                })
            games_json.append(game_json)

        return games_json
