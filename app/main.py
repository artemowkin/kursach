from argparse import ArgumentParser

from fastapi import FastAPI
import uvicorn

from app.utils.init_db import DBInitiator
from app.app.settings import settings


parser = ArgumentParser()

parser.add_argument('--host', type=str, default='0.0.0.0')

parser.add_argument('--port', type=int, default=8000)


app = FastAPI(docs_url='/docs', redoc_url=None)


@app.on_event('startup')
async def on_startup():
    db_initiator = DBInitiator(settings.database_url)
    await db_initiator.init()


if __name__ == '__main__':
    args = parser.parse_args()
    uvicorn.run('app.main:app', host=args.host, port=args.port, reload=True)
