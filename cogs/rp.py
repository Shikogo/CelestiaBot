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

conn = sqlite3.connect('./data/pathfinder.db')
conn.row_factory = sqlite3.Row

class RP:
    """Contains commands useful for roleplaying."""

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def rollscores(self, ctx):
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

        await ctx.send(result)

    @commands.group(aliases = ['swxp'])
    async def sw_xp(self, ctx):
        """ Displays XP from the shipwrecked campaign. """
        if ctx.invoked_subcommand is None:
            with open('./data/sw_xp.json') as f:
                xp = json.load(f)

            await ctx.send("The current XP total is **{0}**. The last XP gain was {1} on {2}.".format(xp[0], xp[1], xp[2]))

    @sw_xp.command()
    @checks.is_mod()
    async def add(self, ctx, gain: int):
        """ Adds XP. Mod only. """
        with open('./data/sw_xp.json') as f:
            xp = json.load(f)

        xp[0] += gain                               # add new XP to total and save
        xp[1] = gain                                # save most recent gain
        xp[2] = dt.date.today().strftime("%B %d")   # save formatted date as string

        with open('./data/sw_xp.json', 'w') as f:
            json.dump(xp, f)

        await ctx.send("**{1}** XP added. New total: {0}.".format(xp[0], xp[1]))

    @commands.command()
    async def pathfinder(self, ctx, *, spell):
        """ Retrieves information about a spell in pathfinder. """

        spell_data = conn.execute("SELECT * FROM spells WHERE name LIKE ?", (spell,)).fetchone()

        if spell_data:

            desc_soup = BeautifulSoup(spell_data["description_formated"], "html.parser")
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

            await ctx.send(output + desc)


        else:
            await ctx.send("I didn't find anything!")

    @commands.command()
    async def pf_search(self, ctx, search):
        """ Searching for Pathfinder spells, I guess."""

        spell_list = conn.execute("SELECT name FROM spells WHERE name LIKE ?", ("%{}%".format(search),)).fetchall()

        if spell_list:
            search_results = ", ".join(spell[0] for spell in spell_list)
            await ctx.send("Search results: {}".format(search_results))

        else:
            await ctx.send("Nothing found.")


    @commands.command()
    async def roll_range(self, ctx, x: int, y: int):
        """ Generates a random number between x and y """

        if x >= y:
            await ctx.send("The first number needs to be smaller than the second!")

        else:
            random_number = random.randint(x, y)
            await ctx.send("Your random number is: {}".format(random_number))



def setup(bot):
    bot.add_cog(RP(bot))
