import hikari
import tanjun

from hikari_testing.bot.client import Client
from hikari_testing.bot import bot as hikari_bot

component = tanjun.Component(name="owneronly")


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option("module", "The module you want to Reload")
@tanjun.as_slash_command("reloadload", "Reload a module")
async def reload_module(ctx: tanjun.abc.Context, module: str) -> None:
    for component in ctx.client.components:
        if component.name == module:
            ctx.client.remove_component(component)
            ctx.client.add_component(component)

            await ctx.respond("Reloaded the component!")
            return

    await ctx.respond(f"I couldn't find a component with the name `{module}`")


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option("module", "The module you want to unload")
@tanjun.as_slash_command("unload", "Unload the module")
async def unload(ctx: tanjun.abc.Context, module: str) -> None:
    pass


@tanjun.as_slash_command("unload", "Unload the ")
@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
