# The code for this file is a modified version of https://github.com/Carberra/Carberretta/blob/master/carberretta/db/db.py made by Ethan Henderson (Carberra)

import os

from aiofiles import open
import aiosqlite
from apscheduler.triggers.cron import CronTrigger


class Database:
    def __init__(self, scheduler):
        self.path = f"data/db/database.db3"
        self.build_path = f"data/db/build.sql"
        self._calls = 0

        scheduler.add_job(self.commit, CronTrigger(second=0))

    async def connect(self):
        self.cxn = await aiosqlite.connect(self.path)
        await self.executescript(self.build_path)
        await self.commit()

    async def commit(self):
        await self.cxn.commit()

    async def close(self):
        await self.commit()
        await self.cxn.close()

    async def sync(self):
        await self.commit()

    async def field(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        if (row := await cur.fetchone()) is not None:
            return row[0]

    async def record(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return await cur.fetchone()

    async def records(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return await cur.fetchall()

    async def column(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return [row[0] for row in await cur.fetchall()]

    async def execute(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return cur.rowcount

    async def executemany(self, command, valueset):
        cur = await self.cxn.executemany(command, valueset)
        self._calls += 1

        return cur.rowcount

    async def executescript(self, path, **kwargs):
        async with open(path, "r", encoding="utf-8") as script:
            await self.cxn.executescript((await script.read()).format(**kwargs))

        self._calls += 1
