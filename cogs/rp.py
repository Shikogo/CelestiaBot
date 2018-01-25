import asyncio
import datetime as dt
import json
import random
import sqlite3
import pickle

from bs4 import BeautifulSoup

import discord
from discord.ext import commands

import checks

conn = sqlite3.connect('database/pathfinder.db')
conn.row_factory = sqlite3.Row

class RP:
    """Contains commands useful for roleplaying."""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(hidden=True)
    async def rollscores(self):
        """
        Generates ability scores based on the default pathfinder system.
        """

        def output(ability, value):
            return "**{0}**: {1[1]}+{1[2]}+{1[3]} = **{2}** *(discard {1[0]})*\n".format(ability, value, sum(value))

        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence",\
                    "Wisdom", "Charisma"]

        values = [sorted([random.randint(1,6) for x in range(4)]) for x in range(6)]

        result = ""

        for i in range(6):
            result += output(abilities[i], values[i])

        await self.bot.say(result)

    @commands.group(pass_context=True, aliases = ['swxp'])
    async def sw_xp(self, ctx):
        """ Displays XP from the shipwrecked campaign. """
        if ctx.invoked_subcommand is None:
            with open('database/sw_xp.json') as f:
                xp = json.load(f)

            await self.bot.say("The current XP total is **{0}**. The last XP gain was {1} on {2}.".format(xp[0], xp[1], xp[2]))

    @sw_xp.command()
    @checks.is_me_or_mod()
    async def add(self, gain: int):
        """ Adds XP. Mod only. """
        with open('database/sw_xp.json') as f:
            xp = json.load(f)

        xp[0] += gain                               # add new XP to total and save
        xp[1] = gain                                # save most recent gain
        xp[2] = dt.date.today().strftime("%B %d")   # save formatted date as string

        with open('database/sw_xp.json', 'w') as f:
            json.dump(xp, f)

        await self.bot.say("**{1}** XP added. New total: {0}.".format(xp[0], xp[1]))

    @commands.command()
    async def pathfinder(self, *, spell):
        """ Retrieves information about a spell in pathfinder. """

        spell_data = conn.execute("SELECT * FROM spells WHERE name LIKE ?", (spell,)).fetchone()

        if spell_data:

            desc_soup = BeautifulSoup(spell_data["description_formated"])
            for p in desc_soup.findAll("p"):
                p.insert_after(desc_soup.new_string("\n\n"))
            desc = desc_soup.get_text()


            output = (
                "**{name}**\n\n"

                "**School** {school}; **Level** {spell_level}\n\n"

                "**Casting Time** {casting_time}\n**Components** {components}\n\n"

                "**Range** {range}\n**Target** {targets}\n**Duration** {duration}\n"
                "**Saving Throw** {saving_throw}; **Spell Resistance** {spell_resistence}\n\n".format(**spell_data)
                )

            await self.bot.say(output + desc)


        else:
            await self.bot.say("I didn't find anything!")

    @commands.command()
    async def pf_search(self, search):
        """ Searching for Pathfinder spells, I guess."""

        spell_list = conn.execute("SELECT name FROM spells WHERE name LIKE ?", ("%{}%".format(search),)).fetchall()

        if spell_list:
            search_results = ", ".join(spell[0] for spell in spell_list)
            await self.bot.say("Search results: {}".format(search_results))

        else:
            await self.bot.say("Nothing found.")


    @commands.command()
    async def roll_range(self, x: int, y: int):
        """ Generates a random number between x and y """

        if x >= y:
            await self.bot.say("The first number needs to be smaller than the second!")

        else:
            random_number = random.randint(x, y)
            await self.bot.say("Your random number is: {}".format(random_number))



def setup(bot):
    bot.add_cog(RP(bot))
