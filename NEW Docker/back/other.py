import asyncio

from pydantic import BaseModel

from nhl_parser import NhlParser

# константы
user = 'postgres'
password = '6661313w'
server = 'database'
port = '5432'
database_name = 'postgres'


async def create_parser():
    # создание парсера
    db_url = f'postgres://{user}:{password}@{server}:{port}/{database_name}'
    # db_url='sqlite://db.sqlite3'
    nhl_parser = NhlParser()
    await nhl_parser.init(db_url)
    return nhl_parser


async def parse_games(start_date, end_date):
    # парсинг данных и сохранение их в бд
    nhl_parser = await create_parser()
    teams = await nhl_parser.parse_teams()
    games = await nhl_parser.parse_games_for_teams(teams, start_date, end_date)
    for game in games:
        await nhl_parser.parse_game_data_and_save(game)


async def get_data(start_date, end_date):
    # сборка данных из бд
    nhl_parser = await create_parser()
    return await nhl_parser.get_data(start_date, end_date)


async def parse_games_sync(start_date, end_date):
    return await parse_games(start_date, end_date)


async def get_data_sync(start_date, end_date):
    return await get_data(start_date, end_date)


class DateRegion(BaseModel):
    start_date: str
    end_date: str