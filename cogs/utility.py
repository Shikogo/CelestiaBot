import asyncio
import aiohttp
import configparser
import json
import random

import discord
from discord.ext import commands
import derpibooru as d

import checks

config = configparser.ConfigParser()
config.read("config.ini")


class Utility:
    """Contains utility commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def botspam(self, ctx, *members: discord.Member):
        """
        For when bot usage gets spammy.
        Can be called with an arbitrary number of users as arguments.
        Each of the users listed gets automatically pinged in the bot room.
        """

        server_id = ctx.message.server.id

        servers = {
        #   Server ID           : bot channel ID
            "146965094998212608": "174963303527874561", # mlpds
            "178176831508316160": "209122538368794624"  # the blastradius
        }

        if server_id in servers.keys():
            bot_channel = self.bot.get_channel(servers[server_id])
            bot_channel_name = bot_channel.mention
        else:
            bot_channel = None
            bot_channel_name = "the bot channel"

        await self.bot.say("Spam spam spam! Please continue in {}.".format(bot_channel_name))

        if bot_channel:
            if members:
                await self.bot.send_message(bot_channel,
                    "You can play with us here, {}! [](/lcefilly)".format(
                    ", ".join([x.mention for x in members])
                    ))
            else:
                await self.bot.send_message(bot_channel, "You can play with us here! [](/lcefilly)")

    @commands.command()
    @checks.is_me()
    async def logout(self):
        """Turns off/restarts the bot."""
        await self.bot.say("Shutting down.")
        await self.bot.logout()


    @commands.command()
    @checks.is_me()
    async def set_game(self, game=None):
        """Sets the game the bot is 'playing'."""
        await self.bot.change_presence(game = discord.Game(name = game))
        await self.bot.say("Game set to {}.".format(game))

    @commands.command(pass_context=True)
    @checks.is_me()
    async def set_nick(self, ctx, name=None):
        """Allows the owner to change the display name of the bot."""
        await self.bot.change_nickname(ctx.message.server.me, name)
        if name:
            await self.bot.say("Changed display name to {}.".format(name))
        else:
            await self.bot.say("Name reset.")

    @commands.command(hidden=True)
    @checks.is_me()
    async def echo(self, *, msg):
        """
        Returns the message entered.
        Can only be used by the bot owner.
        """
        await self.bot.say(msg)

    @commands.command(hidden=True)
    @checks.is_me()
    async def secho(self, channel, *, msg):
        """ Sends a message into a chosen channel. """
        await self.bot.send_message(discord.Object(channel), msg)
        await self.bot.say("Message sent.")

    @commands.group(pass_context=True, hidden=True)
    @checks.is_me()
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
                    unidentified.append(user_id)
            if names:
                await self.bot.say("These are the users currently blacklisted: {}".format(', '.join(names)))
            else:
                await self.bot.say("Currently there are no blacklisted users.")
            if unidentified:
                await self.bot.say("I also found these IDs, but don't know who they are: {}".format(', '.join(unidentified)))

    @blacklist.command(pass_context=True)
    async def server(self, ctx):
        names = []
        for user_id in checks.blacklist:
            user = ctx.message.server.get_member(user_id)
            if user:
                names.append(user.name)
        if names:
            await self.bot.say("These are the users currently blacklisted on this server: {}".format(', '.join(names)))
        else:
            await self.bot.say("Currently there are no blacklisted users on this server.")

    @blacklist.command()
    async def add(self, user: discord.Member):
        if user.id not in checks.blacklist:
            checks.blacklist.add(user.id)
            with open('blacklist.json', 'w') as f:
                json.dump(list(checks.blacklist), f)
            await self.bot.say("{} added to the blacklist.".format(user.name))
        else:
            await self.bot.say("That user is already blacklisted.")

    @blacklist.command()
    async def remove(self, user: discord.Member):
        if user.id in checks.blacklist:
            checks.blacklist.remove(user.id)
            with open('blacklist.json', 'w') as f:
                json.dump(list(checks.blacklist), f)
            await self.bot.say("Removed {} from the blacklist.".format(user.name))
        else:
            await self.bot.say("That user isn't even blacklisted!")

    @commands.command(aliases=['mlpw'])
    async def mlpwiki(self, *, search):
        """Searches the MLP wiki and returns the first link."""
        search_processed = search.replace(" ", "+")
        async with aiohttp.ClientSession() as session:
            async with session.get('http://mlp.wikia.com/api/v1/Search/List?query={}&limit=1&minArticleQuality=10&batch=1&namespaces=0%2C14'.format(search_processed)) as resp:
                try:
                    search_result = await resp.json()
                    article_url = search_result['items'][0]['url']
                except KeyError:
                    await self.bot.say("No search result found.")
                    return

        await self.bot.say("{}".format(article_url))


    @commands.group(pass_context=True, hidden=True)
    async def derpi(self, ctx):
        """ Derpibooru shenanigans. """
        if ctx.invoked_subcommand is None:
            result = next(d.Search().limit(1).sort_by(d.sort.RANDOM).query("safe"))
            await self.bot.say("Here's a random safe Derpibooru image: {}".format(result.url))

    @derpi.command()
    @checks.is_me()
    async def all(self):
        result = next(d.Search().limit(1).sort_by(d.sort.RANDOM).key("sBUN4LM8cLj2ze_2rj7R"))
        await self.bot.say("Here's a random Derpibooru image: {}".format(result.url))


def setup(bot):
    bot.add_cog(Utility(bot))
