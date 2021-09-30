import typing as t

import hikari
import tanjun
from hikari_testing.bot.client import Client

component = tanjun.Component(name="mod")


@component.with_slash_command
@tanjun.with_author_permission_check(hikari.Permissions.KICK_MEMBERS)
@tanjun.with_own_permission_check(hikari.Permissions.KICK_MEMBERS)
@tanjun.with_member_slash_option("member", "The member to kick")
@tanjun.with_str_slash_option(
    "reason", "The reason for kicking the member", default="No reason provided"
)
@tanjun.as_slash_command("kick", "Kick a member from the server")
async def kick(
    ctx: tanjun.abc.Context, member: hikari.Member, reason: t.Optional[str]
) -> None:
    try:
        await member.kick(reason=reason)
    except hikari.errors.InternalServerError:
        try:
            await ctx.respond("Something went wrong on discords end!")
        except:
            pass
    else:
        await ctx.respond(f"Kicked {member.mention} for `{reason}`")


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
