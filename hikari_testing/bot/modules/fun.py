import asyncio
import random

import hikari
import tanjun
from hikari.interactions.base_interactions import ResponseType
from hikari_testing.bot import bot
from hikari_testing.bot.client import Client

component = tanjun.Component(name="fun")


EMBED_MENU = {
    "📋": {"title": "Title", "style": hikari.ButtonStyle.SECONDARY},
    "💬": {"title": "Description", "style": hikari.ButtonStyle.SECONDARY},
    "🗨️": {"title": "Message", "style": hikari.ButtonStyle.SECONDARY},
    "📌": {
        "title": "Pin",
        "style": hikari.ButtonStyle.SECONDARY,
    },
    "❌": {"title": "Cancel", "style": hikari.ButtonStyle.DANGER},
}

embed = component.with_slash_command(
    tanjun.slash_command_group("embed", "Work with Embeds!", default_to_ephemeral=False)
)


@embed.with_command
@tanjun.as_slash_command("custom", "Make a custom embed using my interactive setup!")
async def custom_embed(ctx: tanjun.abc.SlashContext) -> None:
    building_embed = hikari.Embed(title="New Embed")

    await embed_builder_loop(ctx, building_embed)


async def embed_builder_loop(
    ctx: tanjun.abc.SlashContext, building_embed: hikari.Embed
):
    client = ctx.client
    menu = build_menu(ctx)
    client.metadata["embed"] = building_embed
    client.metadata["message"] = ""
    client.metadata["pin"] = False

    await ctx.edit_initial_response(
        "Click/Tap your choice below, then watch the embed update!",
        embed=client.metadata["embed"],
        components=[*menu],
    )
    try:
        async with bot.stream(hikari.InteractionCreateEvent, timeout=60).filter(
            ("interaction.user.id", ctx.author.id)
        ) as stream:
            async for event in stream:
                key = event.interaction.custom_id
                selected = EMBED_MENU[key]

                if selected["title"] == "Cancel":
                    await ctx.edit_initial_response(content=f"Exiting!", components=[])
                    await asyncio.sleep(2)
                    message = await ctx.edit_initial_response(
                        content=client.metadata["message"], components=[]
                    )

                    if client.metadata["pin"]:
                        channel = await bot.rest.fetch_channel(ctx.channel_id)
                        await channel.pin_message(message.id)

                    return

                await event.interaction.create_initial_response(
                    ResponseType.DEFERRED_MESSAGE_UPDATE,
                )

                await globals()[f"{selected['title'].lower().replace(' ', '_')}"](ctx)
                await ctx.edit_initial_response(
                    "Click/Tap your choice below, then watch the embed update!",
                    embed=client.metadata["embed"],
                    components=[*menu],
                )
    except asyncio.TimeoutError:
        await ctx.edit_initial_response(
            "Waited for 60 seconds... Timeout.", embed=None, components=[]
        )


def build_menu(ctx: tanjun.abc.SlashContext):
    menu = list()
    menu_count = 0
    last_menu_item = list(EMBED_MENU)[-1]
    row = ctx.rest.build_action_row()
    for emote, options in EMBED_MENU.items():
        (
            row.add_button(options["style"], emote)
            .set_label(options["title"])
            .set_emoji(emote)
            .add_to_container()
        )
        menu_count += 1
        if menu_count == 5 or last_menu_item == emote:
            menu.append(row)
            row = ctx.rest.build_action_row()
            menu_count = 0

    return menu


async def title(ctx: tanjun.abc.SlashContext):
    embed_dict, *_ = bot.entity_factory.serialize_embed(ctx.client.metadata["embed"])
    await ctx.edit_initial_response(content="Set Title for embed:", components=[])
    try:
        async with bot.stream(hikari.GuildMessageCreateEvent, timeout=60).filter(
            ("author", ctx.author)
        ) as stream:
            async for event in stream:
                embed_dict["title"] = event.content[:200]
                ctx.client.metadata["embed"] = bot.entity_factory.deserialize_embed(
                    embed_dict
                )
                await ctx.edit_initial_response(
                    content="Title updated!",
                    embed=ctx.client.metadata["embed"],
                    components=[],
                )
                await event.message.delete()
                return
    except asyncio.TimeoutError:
        await ctx.edit_initial_response(
            "Waited for 60 seconds... Timeout.", embed=None, components=[]
        )


async def description(ctx: tanjun.abc.SlashContext) -> None:
    embed_dict, *_ = bot.entity_factory.serialize_embed(ctx.client.metadata["embed"])
    await ctx.edit_initial_response(content="Set Description for embed:", components=[])

    try:
        async with bot.stream(hikari.GuildMessageCreateEvent, timeout=60).filter(
            ("author", ctx.author)
        ) as stream:
            async for event in stream:
                embed_dict["description"] = event.content[:200]
                ctx.client.metadata["embed"] = bot.entity_factory.deserialize_embed(
                    embed_dict
                )

                await ctx.edit_initial_response(
                    content="Title updated!",
                    embed=ctx.client.metadata["embed"],
                    components=[],
                )
                await event.message.delete()
                return
    except asyncio.TimeoutError:
        await ctx.edit_initial_response(
            "Waited for 60 seconds... Timeout.", embed=None, components=[]
        )


async def message(ctx: tanjun.abc.SlashContext) -> None:
    await ctx.edit_initial_response(
        content="Set a message to go along with the embed:", components=[]
    )

    try:
        async with bot.stream(hikari.GuildMessageCreateEvent, timeout=60).filter(
            ("author", ctx.author)
        ) as stream:
            async for event in stream:
                ctx.client.metadata["message"] = event.content[:200]

                await ctx.edit_initial_response(
                    content="Message updated!",
                    embed=ctx.client.metadata["embed"],
                    components=[],
                )
                await event.message.delete()
                return
    except asyncio.TimeoutError:
        await ctx.edit_initial_response(
            "Waited for 60 seconds... Timeout.", embed=None, components=[]
        )


async def pin(ctx: tanjun.abc.SlashContext) -> None:
    ctx.client.metadata["pin"] = not ctx.client.metadata["pin"]


@component.with_slash_command
@tanjun.with_str_slash_option("message", "The message for me to send")
@tanjun.as_slash_command("say", "Make me say a message")
async def say_command(ctx: tanjun.abc.SlashContext, message: str) -> None:
    await ctx.respond(message, user_mentions=True, role_mentions=True)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
