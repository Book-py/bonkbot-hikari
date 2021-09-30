import datetime
import logging
import traceback
import typing as t
from pathlib import Path

import hikari
from hikari_testing import STDOUT_CHANNEL_ID, TEST_GUILD_ID, __version__
import lavasnek_rs

from .client import Client

_BotT = t.TypeVar("_BotT", bound="Bot")


class Bot(hikari.GatewayBot):
    __slots__ = hikari.GatewayBot.__slots__ + ("client", "stdout_channel", "_token")

    def __init__(self: _BotT) -> None:
        with open("hikari_testing/token.0") as f:
            self._token = token = f.read().strip("\n")

        super().__init__(
            token=token,
            intents=hikari.Intents.ALL,
        )

    def create_client(self: _BotT) -> None:
        self.client = Client.from_gateway_bot(self, set_global_commands=TEST_GUILD_ID)
        self.client.load_modules()

    def run(self: _BotT) -> None:
        self.create_client()

        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)

        super().run(
            activity=hikari.Activity(
                name=f"/help | Version {__version__}",
                type=hikari.ActivityType.WATCHING,
            )
        )

    async def on_started(self: _BotT, event: hikari.StartedEvent) -> None:
        self.client.scheduler.start()

        self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        await self.stdout_channel.send(
            embed=hikari.Embed(
                title="Now online",
                description=f"Testing bot v{__version__} now online!",
            )
        )

        logging.info("Bot ready")

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        # This is gonna be fixed.
        await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")
        self.client.scheduler.shutdown()
