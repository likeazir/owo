import asyncio
import colorsys
import random
import time
import discord
from discord.ext import commands, tasks

from owobot.misc import common
from owobot.misc.database import RainbowGuild


class Rainbow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @staticmethod
    def wrap(val):
        if val >= 1.0:
            return val - int(val)
        return val

    @staticmethod
    def gen_colors(num_colors):
        colors = []
        rand = random.random()
        for i in range(num_colors):
            rgb = colorsys.hsv_to_rgb(
                Rainbow.wrap(rand + (1.0 / num_colors) * i), 0.52, 1.0
            )
            colors.append([int(255 * x) for x in rgb])
        return colors

    @commands.group()
    async def rainbowroles(self, ctx):
        pass

    @rainbowroles.command(name="activate", brief="taste the rainbow")
    async def activate(self, ctx):
        await self._activate(ctx.guild)
        await common.react_success(ctx)
        await ctx.channel.send("Created roles, awaiting topping")

    @staticmethod
    async def _activate(guild):
        members = sorted(guild.members, key=lambda m: str(m.display_name.lower()))
        num_colors = len(members)
        colors = Rainbow.gen_colors(num_colors)
        for (member, color, i) in zip(members, colors, range(0, num_colors)):
            try:
                role = await guild.create_role(
                    name=f"rainbowify_{color}",
                    color=discord.Color.from_rgb(*color),
                    hoist=False,
                )
                await member.add_roles(role, reason="owo")
                time.sleep(0.1)
            except Exception as ex:
                print(f"{color}, aaaa, {ex}")

    @rainbowroles.command(name="deactivate", brief="delete all rainbow roles")
    async def deactivate(self, ctx):
        await self._deactivate(ctx.guild)
        await common.react_success(ctx)
        await ctx.channel.send("Until the next rainbow :>")

    @staticmethod
    async def _deactivate(guild):
        for role in guild.roles:
            if role.name.startswith("rainbowify"):
                try:
                    await role.delete()
                except Exception as ex:
                    print(f"aaa {ex}")

    @rainbowroles.command(
        name="top", brief="shuffle all rainbow roles to the second topmost position"
    )
    async def top(self, ctx):
        await self._top(ctx.guild)
        await common.react_success(ctx)
        await ctx.channel.send("Successfully did the topping, please come again!")

    @staticmethod
    async def _top(guild):
        roles = {}
        highest = 0
        for role in guild.me.roles:
            pos = role.position
            if pos > highest:
                highest = pos
        for role in guild.roles:
            if role.name.startswith("rainbowify"):
                roles[role] = highest - 1
        print(roles)
        await guild.edit_role_positions(roles)

    @tasks.loop(hours=24)
    async def schedule_refresh_rainbow(self):
        await asyncio.sleep(common.seconds_until(4, 30))
        await self.refresh_rainbow()

    async def refresh_rainbow(self):
        for rgb_id in RainbowGuild.select():
            guild = self.bot.get_guild(rgb_id.snowflake)
            await self._deactivate(guild)
            await self._activate(guild)
            await self._top(guild)

    @rainbowroles.command(name="refresh", brief="refresh rainbow roles")
    async def refresh(self, ctx):
        await self.refresh_rainbow()


def setup(bot):
    bot.add_cog(Rainbow(bot))
