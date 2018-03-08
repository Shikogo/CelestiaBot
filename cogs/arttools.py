import checks
from discord.ext import commands

from data.models import Pony, select, db_session, set_sql_debug


class ArtTools:
    """Contains tools to use for artists."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['pdb'], hidden=True)
    async def pony_database(self, ctx, *, pony="random"):
        """
        Find a pony in the pony database. If no name is given, get a random pony.

        A bold name means the name is official.
        """

        if pony == "random":
            with db_session:
                result = Pony.select_random(1)[0]
        else:
            with db_session:
                result = select(p for p in Pony if p.name.lower() == pony.lower()).first()
                if not result:
                    result = select(p for p in Pony if pony.lower() in p.name.lower()).first()

        if result:
            if result.official:
                name = "**{}**".format(result.name)
            else:
                name = result.name
            if result.first_appearance:
                try:
                    first_app = "Season {}, Episode {}, {} minutes {} seconds".format(*result.first_appearance.split("|"))
                except IndexError:
                    first_app = result.first_appearance
            else:
                first_app = "None"

            if result.link:
                url = "Wiki: <{}>\n".format(result.link)
            else:
                url = ""

            output =    ("{name}, {r.group}, {r.kind}\n\n"
                        "Coat Color:    {r.coat_color_name} ( {r.coat_color} )\n"
                        "Mane Color:  {r.mane_color_name} ( {r.mane_color} )\n"
                        "Eye Color:      {r.eye_color_name} ( {r.eye_color}  )\n\n"

                        "First Appearance: {first_app}.\n\n"

                        "{url}{r.image}".format(r=result, name=name, first_app=first_app, url=url))

            await ctx.send(output)

        else:
            await ctx.send("No pony of that name found.")
    #
    #
    # @commands.command(hidden=True)
    # async def pdb_search(self, ctx, *args):
    #     """
    #     Allows advanced searching of the pony database.
    #
    #     use &pdb_search -h for more info.
    #     """
    #
    #     parser = argparse.ArgumentParser(prog="&pdb_search", description="Searches the pony database.")
    #
    #     parser.add_argument('--name', '-n')
    #     parser.add_argument('--kind', '-k')
    #     parser.add_argument('--category', '-c')
    #
    #     try:
    #         result = parser.parse_args(args)
    #     except SystemExit:
    #         usage = parser.format_help()
    #         await ctx.send(usage)
    #         return
    #
    #     name, kind, category = "%", "%", "%"
    #
    #     if result.name:
    #         name = result.name
    #     if result.kind:
    #         kind = result.kind
    #     if result.category:
    #         category = result.category
    #
    #
    #     result = conn.execute('SELECT * FROM ponies WHERE name LIKE ? AND kind LIKE ? AND category LIKE ?', (name, kind, category)).fetchone()
    #
    #     if result:
    #         await ctx.send(result['name'])
    #     else:
    #         await ctx.send("Nope")
    #
    #
    # @commands.command(aliases = ["randompony"])
    # async def rpony(self, ctx):
    #     """ Returns a random pony. """
    #
    #     result = conn.execute('SELECT * FROM ponies ORDER BY RANDOM() LIMIT 1;').fetchone()
    #
    #     if result['link']:
    #         link_format = "Link: <{}>\n".format(result['link'])
    #     else:
    #         link_format = ""
    #
    #     output = ("**{name}**\n{link_format}{image}".format(**result, link_format=link_format))
    #
    #     await ctx.send(output)


def setup(bot):
    bot.add_cog(ArtTools(bot))
