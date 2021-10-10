import contextlib
import io
import textwrap
import traceback

import hikari
import tanjun
from hikari_testing.bot import bot as hikari_bot
from hikari_testing.bot.client import Client
from hikari_testing.utils import OwnerUtils

component = tanjun.Component(name="owneronly")


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option("module", "The module you want to Reload")
@tanjun.as_slash_command("reloadload", "Reload a module")
async def reload_module(ctx: tanjun.abc.Context, module: str) -> None:
    # Waiting for the ability to reload modules to be added!
    pass


@component.with_slash_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option("module", "The module you want to unload")
@tanjun.as_slash_command("unload", "Unload the module")
async def unload(ctx: tanjun.abc.Context, module: str) -> None:
    # Waiting for the ability to reload modules to be added!
    pass


@component.with_command
@tanjun.with_greedy_argument("code")
@tanjun.with_parser
@tanjun.with_owner_check()
@tanjun.as_message_command("eval")
async def eval_command(ctx: tanjun.abc.Context, code: str) -> None:
    code = OwnerUtils.clean_code(code)
    local_variables = {
        "bot": hikari_bot,
        "hikari": hikari,
        "tanjun": tanjun,
        "client": ctx.client,
        "ctx": ctx,
    }
    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(f"async def func():\n{textwrap.indent(code, '    ')}", local_variables)

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(traceback.format_exc())

    embed = hikari.Embed(title="Your evaluated code", description=f"```py\n{result}```")
    await ctx.respond(embed)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
