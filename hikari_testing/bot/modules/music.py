import datetime
import logging
import typing as t

import hikari
import lavasnek_rs
import tanjun
from hikari_testing.bot import bot as hikari_bot
from hikari_testing.bot import lavasnek_eventhandler
from hikari_testing.bot.client import Client

component = tanjun.Component(name="music")


async def on_starting(event: hikari.StartingEvent) -> None:
    with open("hikari_testing/token.0") as f:
        token = f.read().strip("\n")

    builder = (
        # TOKEN can be an empty string if you don't want to use lavasnek's discord gateway.
        lavasnek_rs.LavalinkBuilder(820335303386595381, token)
        # This is the default value, so this is redundant, but it's here to show how to set a custom one.
        .set_host("127.0.0.1")
    )

    Client.lavalink = await builder.build(lavasnek_eventhandler.EventHandler())
    logging.info("Created lavalink instance")


hikari_bot.event_manager.subscribe(hikari.StartingEvent, on_starting)


@component.with_slash_command
@tanjun.with_guild_check
@tanjun.with_channel_slash_option(
    "channel", "The channel to join if you aren't in a voice channel", default=None
)
@tanjun.as_slash_command("join", "Join a voice channel")
async def join_command(
    ctx: tanjun.abc.SlashContext, channel: t.Optional[hikari.GuildVoiceChannel]
) -> None:
    if channel:
        connection_info = await Client.lavalink.join(ctx.guild_id, channel.id)
        await Client.lavalink.create_session(connection_info)
        await ctx.respond(f"Joined <#{channel.id}>")


@component.with_slash_command
@tanjun.with_str_slash_option("link", "The link to the music to listen to")
@tanjun.as_slash_command("play", "Play music in a voice channel")
async def play_music_command(ctx: tanjun.abc.SlashContext, link: str) -> None:
    query_information = await Client.lavalink.auto_search_tracks(link)
    print(
        f"query_information.tracks: {query_information.tracks}\nType: {type(query_information.tracks)}"
    )
    if not query_information.tracks:
        await ctx.respond(
            "Couldn't find any video for the specified link or search query"
        )
        return

    try:
        await Client.lavalink.play(ctx.guild_id, query_information.tracks[0]).requester(
            ctx.author.id
        ).queue()

        track_info = query_information.tracks[0].info
        embed = hikari.Embed(
            title="Added to the queue",
            colour=0x0FFF00,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )

        fields = [
            ("Title", track_info.title, True),
            ("Author", track_info.author, True),
            ("Duration", track_info.length, True),
            ("Stream", track_info.is_stream, True),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.respond(embed)
    except lavasnek_rs.NoSessionPresent:
        await ctx.respond("Couldn't find a lavalink session")
        return


@component.with_slash_command
@tanjun.as_slash_command("leave", "Stop playing music and leave the voice channel")
async def leave_vc(ctx: tanjun.abc.SlashContext) -> None:
    await Client.lavalink.destroy(ctx.guild_id)
    await Client.lavalink.leave(ctx.guild_id)

    await ctx.respond("Left voice channel")


@component.with_slash_command
@tanjun.as_slash_command("stop", "Stop playing music")
async def stop_playing_music(ctx: tanjun.abc.SlashContext) -> None:
    await Client.lavalink.stop(ctx.guild_id)
    await ctx.send("Stopped playing music!")


@component.with_slash_command
@tanjun.as_slash_command("pause", "Pause the music playing")
async def pause_music(ctx: tanjun.abc.SlashContext) -> None:
    await Client.lavalink.pause(ctx.guild_id)
    await ctx.respond("Paused the playing music!")


@component.with_slash_command
@tanjun.as_slash_command(
    "resume", "Resume playing the music that played before pausing."
)
async def resume_music(ctx: tanjun.abc.SlashContext) -> None:
    await Client.lavalink.resume(ctx.guild_id)
    await ctx.respond("Resumed playing the music")


@component.with_slash_command
@tanjun.as_slash_command("queue", "See the music queue.")
async def music_queue(ctx: tanjun.abc.SlashContext) -> None:
    pass


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
