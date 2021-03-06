import asyncio
import aiohttp
import configparser
import json
import random

import discord
from discord.ext import commands
import derpibooru as d
import aiofiles

import checks

config = configparser.ConfigParser()
config.read("config.ini")

source = config['Bot']['source_url']

timers = {}


class Utility:
    """Contains utility commands."""

    def __init__(self, bot):
        self.bot = bot
        try:
            with open("./data/servers.json") as f:
                self.servers = json.load(f)
        except FileNotFoundError:
            self.servers = {}

    @commands.command()
    async def botspam(self, ctx, *members: discord.Member):
        """
        For when bot usage gets spammy.
        Can be called with an arbitrary number of users as arguments.
        Each of the users listed gets automatically pinged in the bot room.
        """

        servers= {}

        server_id = str(ctx.message.guild.id)

        if server_id in self.servers.keys():
            bot_channel = self.bot.get_channel(self.servers[server_id])
            bot_channel_name = bot_channel.mention
        else:
            bot_channel = None
            bot_channel_name = "the bot channel"

        await ctx.send("Spam spam spam! Please continue in {}.".format(bot_channel_name))

        if bot_channel:
            if members:
                await bot_channel.send("You can play with us here, {}! [](/lcefilly)".format(", ".join([x.mention for x in members])))
            else:
                await bot_channel.send("You can play with us here! [](/lcefilly)")

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        """Turns off/restarts the bot."""
        await ctx.send("Shutting down.")
        await self.bot.logout()


    @commands.command()
    @commands.is_owner()
    async def set_game(self, ctx, *, game=None):
        """Sets the game the bot is 'playing'."""
        await self.bot.change_presence(activity=discord.Game(name=game))
        await ctx.send("Game set to {}.".format(game))

    @commands.command()
    @commands.is_owner()
    async def set_nick(self, ctx, *, nick=None):
        """Allows the owner to change the display name of the bot."""
        await ctx.me.edit(nick=nick)
        if nick:
            await ctx.send("Changed display name to {}.".format(nick))
        else:
            await ctx.send("Name reset.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def echo(self, ctx, *, msg):
        """
        Returns the message entered.
        Can only be used by the bot owner.
        """
        await ctx.send(msg)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def secho(self, ctx, target_channel: discord.TextChannel, *, msg):
        """ Sends a message into a chosen channel. """
        await target_channel.send(msg)
        await ctx.send("Message sent.")

    @commands.group(hidden=True)
    @checks.is_mod()
    async def blacklist(self, ctx):
        """ Blacklisting tools. """
        if ctx.invoked_subcommand is None:
            names = []
            unidentified = []
            for user_id in checks.blacklist:
                user = discord.utils.get(self.bot.get_all_members(), id=user_id)
                if user:
                    names.append(user.name)
                else:
                    unidentified.append(str(user_id))
            if names:
                await ctx.send("These are the users currently blacklisted: {}".format(", ".join(names)))
            else:
                await ctx.send("Currently there are no blacklisted users.")
            if unidentified:
                await ctx.send("I also found these IDs, but don't know who they are: {}".format(", ".join(unidentified)))

    @blacklist.command()
    async def server(self, ctx):
        names = []
        for user_id in checks.blacklist:
            user = ctx.message.server.get_member(user_id)
            if user:
                names.append(user.name)
        if names:
            await ctx.send("These are the users currently blacklisted on this server: {}".format(", ".join(names)))
        else:
            await ctx.send("Currently there are no blacklisted users on this server.")

    @blacklist.command()
    async def add(self, ctx, user: discord.Member):
        if user.id not in checks.blacklist:
            checks.blacklist.add(user.id)
            async with aiofiles.open("./data/blacklist.json", mode="w") as f:
                await f.write(json.dumps(list(checks.blacklist)))
            await ctx.send("{} added to the blacklist.".format(user.name))
        else:
            await ctx.send("That user is already blacklisted.")

    @blacklist.command(aliases=["rm"])
    async def remove(self, ctx, user: discord.Member):
        if user.id in checks.blacklist:
            checks.blacklist.remove(user.id)
            async with aiofiles.open("./data/blacklist.json", mode="w") as f:
                await f.write(json.dumps(list(checks.blacklist)))
            await ctx.send("Removed {} from the blacklist.".format(user.name))
        else:
            await ctx.send("That user isn't even blacklisted!")

    @commands.command(aliases=['mlpw'])
    async def mlpwiki(self, ctx, *, search):
        """Searches the MLP wiki and returns the first link."""
        search_processed = search.replace(" ", "+")
        async with aiohttp.ClientSession() as session:
            async with session.get('http://mlp.wikia.com/api/v1/Search/List?query={}&limit=1&minArticleQuality=10&batch=1&namespaces=0%2C14'.format(search_processed)) as resp:
                try:
                    search_result = await resp.json()
                    article_url = search_result['items'][0]['url']
                except KeyError:
                    await ctx.send("No search result found.")
                    return

        await ctx.send("{}".format(article_url))


    @commands.group(hidden=True)
    async def derpi(self, ctx):
        """ Derpibooru shenanigans. """
        result = next(d.Search().limit(1).sort_by(d.sort.RANDOM).query("safe"))
        await ctx.send("Here's a random safe Derpibooru image: {}".format(result.url))


    @commands.command()
    async def source(self, ctx):
        """ Links to the source code. """
        owner = (await ctx.bot.application_info()).owner.mention
        await ctx.send("I was made by {}!\n\nYou can find my source code here:\n{}".format(owner, source))


def setup(bot):
    bot.add_cog(Utility(bot))
