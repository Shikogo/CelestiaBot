import argparse
import asyncio
import aiohttp
from difflib import SequenceMatcher
import random
import sqlite3

import checks
from discord.ext import commands

conn = sqlite3.connect('database/ponies.db')
conn.row_factory = sqlite3.Row


class ArtTools:
    """Contains tools to use for artists."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, aliases=['pdb'])
    async def pony_database(self, *, pony="random"):
        """ testing the new pony database """

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

            await self.bot.say(output)

        else:
            await self.bot.say("No pony of that name found.")


    @commands.command(hidden=True)
    async def pdb_search(self, *args):
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
            await self.bot.say(usage)
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
            await self.bot.say(result['name'])
        else:
            await self.bot.say("Nope")


    @commands.command(aliases = ["randompony"])
    async def rpony(self):
        """ Returns a random pony. """

        result = conn.execute('SELECT * FROM ponies ORDER BY RANDOM() LIMIT 1;').fetchone()

        if result['link']:
            link_format = "Link: <{}>\n".format(result['link'])
        else:
            link_format = ""

        output = ("**{name}**\n{link_format}{image}".format(**result, link_format=link_format))

        await self.bot.say(output)


    # @commands.command(aliases = ["cs", "choosestudy"])
    # async def study(self, *, topic="random"):
    #     """
    #     Returns a random topic to study.
    #     Can be called with a topic already selected to return a related link.
    #
    #     List of topics:
    #     anatomy, constructive form, expressions, gesture, composition,
    #     perspective, light and shadow, linework, color theory, master studies
    #
    #     Still under heavy construction.
    #     """
    #     topics = [
    #         ("anatomy", 3),
    #         ("constructive form", 3),
    #         ("expressions", 3),
    #         ("gesture", 3),
    #
    #         ("composition", 2),
    #         ("perspective", 2),
    #         ("light and shadow", 2),
    #         ("linework", 2),
    #
    #         ("color theory", 1),
    #
    #         ("master studies", 2),
    #         ("favorite artist", 3)
    #     ]
    #     links = {
    #         "anatomy": "https://uwdc.library.wisc.edu/collections/Science/VetAnatImgs/",
    #         "constructive form": "http://www.ctrlpaint.com/videos/constructive-form-pt-1",
    #         "expressions": "http://www.lackadaisycats.com/gallery/1295341707.jpg",
    #         "gesture": "https://www.youtube.com/watch?v=74HR59yFZ7Y",
    #
    #         "composition": "https://www.youtube.com/watch?v=aHq5KwFvtns",
    #         "perspective": "https://www.youtube.com/watch?v=0xnfQScu8cE",
    #         "light and shadow": "https://www.youtube.com/watch?v=-dqGkHWC5IU",
    #         "linework": "http://smokinghippo.com/TSOtutes/inking_tutorial.html",
    #
    #         "color theory": "http://drawing-tutorials.deviantart.com/art/How-I-See-Color-A-Tutorial-184642625",
    #
    #         "master studies": "https://en.wikipedia.org/wiki/Old_Master#Incomplete_list_of_the_most_important_Old_Masters"
    #     }
    #
    #     if not any(x[0] == topic for x in topics):
    #         population = [val for val, cnt in topics for i in range(cnt)]
    #         topic = random.choice(population)
    #
    #     if topic == "favorite artist":
    #         await self.bot.say("Study your favorite artist! Just pick a drawing you like and try to figure out how it was done.")
    #     elif topic == "master studies":
    #         await self.bot.say("Take some time to study the old masters. If you don't know how to choose, here are some suggestions: {}.".format(links["master studies"]))
    #         await self.bot.say("If you get stuck, try `?masterstudies`.")
    #     else:
    #         await self.bot.say("Time to study {}! Here's a link to get you started: {}".format(topic, links[topic]))


def setup(bot):
    bot.add_cog(ArtTools(bot))
