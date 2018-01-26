import argparse
import asyncio
import aiohttp
import sqlite3

import checks
from discord.ext import commands

conn = sqlite3.connect('database/ponies.db')
conn.row_factory = sqlite3.Row


class ArtTools:
    """Contains tools to use for artists."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['pdb'], hidden=True)
    async def pony_database(self, ctx, *, pony="random"):
        """ A pony database. Still work in progress. """

        if pony == "random":
            result = conn.execute('SELECT * FROM ponies ORDER BY RANDOM() LIMIT 1;').fetchone()
        else:
            result = conn.execute('SELECT * FROM ponies WHERE name like ?', (pony,)).fetchone()

        if result:
            if result['first_appearance']:
                first_app = "Season {}, Episode {}, {} minutes {} seconds".format(*result['first_appearance'].split("|"))
            else:
                first_app = "Unknown"

            if result['link']:
                url = "Wiki: <{}>\n".format(result['link'])
            else:
                url = ""

            output =    ("**{name}**, {category}, {kind}\n\n"
                        "Coat Color:    {coat_color_name} ( {coat_color} )\n"
                        "Mane Color:  {mane_color_name} ( {mane_color} )\n"
                        "Eye Color:      {eye_color_name} ( {eye_color}  )\n\n"

                        "First Appearance: {first_app}.\n\n"

                        "{url}{image}".format(**result, first_app=first_app, url=url))

            await ctx.send(output)

        else:
            await ctx.send("No pony of that name found.")


    @commands.command(hidden=True)
    async def pdb_search(self, ctx, *args):
        """
        Allows advanced searching of the pony database.

        use &pdb_search -h for more info.
        """

        parser = argparse.ArgumentParser(prog="&pdb_search", description="Searches the pony database.")

        parser.add_argument('--name', '-n')
        parser.add_argument('--kind', '-k')
        parser.add_argument('--category', '-c')

        try:
            result = parser.parse_args(args)
        except SystemExit:
            usage = parser.format_help()
            await ctx.send(usage)
            return

        name, kind, category = "%", "%", "%"

        if result.name:
            name = result.name
        if result.kind:
            kind = result.kind
        if result.category:
            category = result.category


        result = conn.execute('SELECT * FROM ponies WHERE name LIKE ? AND kind LIKE ? AND category LIKE ?', (name, kind, category)).fetchone()

        if result:
            await ctx.send(result['name'])
        else:
            await ctx.send("Nope")


    @commands.command(aliases = ["randompony"])
    async def rpony(self, ctx):
        """ Returns a random pony. """

        result = conn.execute('SELECT * FROM ponies ORDER BY RANDOM() LIMIT 1;').fetchone()

        if result['link']:
            link_format = "Link: <{}>\n".format(result['link'])
        else:
            link_format = ""

        output = ("**{name}**\n{link_format}{image}".format(**result, link_format=link_format))

        await ctx.send(output)


def setup(bot):
    bot.add_cog(ArtTools(bot))
