import typing as t
from pathlib import Path

import tanjun
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from hikari_testing.bot.db import Database
from pytz import utc
import lavasnek_rs

_ClientT = t.TypeVar("_ClientT", bound="Client")


class Client(tanjun.Client):
    __slots__ = tanjun.Client.__slots__ + (
        "scheduler",
        "lavalink",
        "db",
    )

    def __init__(self: _ClientT, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)
        self.lavalink: lavasnek_rs.Lavalink = None

        self.db = Database(self.scheduler)

    def load_modules(self: _ClientT) -> _ClientT:
        return super().load_modules(
            *[
                f"hikari_testing.bot.modules.{m.stem}"
                for m in Path(__file__).parent.glob("modules/*.py")
            ]
        )
        # Fixed in #55, need to wait until @task/components is merged.
        # return super().load_modules(*Path(__file__).parent.glob("modules/*.py"))
