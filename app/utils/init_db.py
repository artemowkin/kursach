from typing import Callable, Any
import json

import psycopg
import termcolor

from app.app.settings import BASE_DIR


def with_connection(func: Callable) -> Callable:

    async def wrapper(self, *args, **kwargs):
        async with await psycopg.AsyncConnection.connect(self.uri) as conn:
            async with conn.cursor() as cursor:
                return await func(self, *args, **kwargs, cursor=cursor)

    return wrapper


class DBInitiator:
    init_config_file = BASE_DIR / 'init.json'

    def __init__(self, uri: str):
        self.uri = uri
        self._config = self._init_config()

    def _init_config(self) -> dict[str, dict[str, Any]]:
        with self.init_config_file.open() as f:
            config_json = json.load(f)
            return config_json

    @property
    def config(self) -> dict[str, dict[str, Any]]:
        if self._config: return self._config

    async def _init_tables(self, cursor: psycopg.AsyncCursor) -> None:
        for tablename, command in self._config['db'].items():
            command = command if isinstance(command, str) else ''.join(command)
            await cursor.execute(command)
            print(f"Table `{tablename}`" + termcolor.colored("created", "green"))

    async def _check_data_already_exists(self, cursor: psycopg.AsyncCursor) -> bool:
        first_table_name = list(self._config['db'].keys())[0]
        result = await cursor.execute(psycopg.sql.SQL('select count(*) from {0};').format(psycopg.sql.Identifier(first_table_name)))
        count = await result.fetchone()
        return count[0] > 0

    async def _init_data(self, cursor: psycopg.AsyncCursor) -> None:
        for tablename, entries in self._config['data'].items():
            for entry in entries:
                query_keys = ", ".join(entry.keys())
                query_values = ', '.join(['%%(%s)s' % x for x in entry])
                command = "insert into {0}({1}) VALUES ({2})".format(
                    tablename, query_keys, query_values
                )
                await cursor.execute(command, entry)

    @with_connection
    async def init(self, cursor: psycopg.AsyncCursor) -> None:
        await self._init_tables(cursor)
        if await self._check_data_already_exists(cursor):
            return

        await self._init_data(cursor)
