import logging


class EventHandler:
    """Events from the Lavalink server"""

    async def track_start(self, _lava_client, event):
        logging.info("Track started on guild: %s", event.guild_id)

    async def track_finish(self, _lava_client, event):
        logging.info("Track finished on guild: %s", event.guild_id)

    async def track_exception(self, lavalink, event):
        logging.warning("Track exception event happened on guild: %d", event.guild_id)

        # If a track was unable to be played, skip it
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not skip:
            await event.message.respond("Nothing to skip")
        else:
            if not node.queue and not node.now_playing:
                await lavalink.stop(event.guild_id)
