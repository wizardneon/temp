import uvicorn
from fastapi import FastAPI
from other import DateRegion, parse_games_sync, get_data_sync

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse/")
def parse(date_region: DateRegion):
    parse_games_sync(date_region.start_date, date_region.end_date)
    return {"ok"}


@app.post("/get/")
def get(date_region: DateRegion):
    return get_data_sync(date_region.start_date, date_region.end_date)


if __name__ == '__main__':
    # before execute:
    # pip install tortoise-orm[asyncpg] requests typing_extensions python-dateutil fastapi uvicorn[standard]
    # execute:
    # python main.py
    uvicorn.run(app, port=8081, host='0.0.0.0')