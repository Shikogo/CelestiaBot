import asyncio
import difflib
import json
import random
import re

import discord
from discord.ext import commands
import derpibooru as d
import aiofiles
import requests

import checks

class Player:
    """Player class for the Derpibooru Game."""

    def __init__(self, user):
        self.user = user
        self.count = 0
        self.wrong = 0

class Tag:
    """Processes guesses."""
    def __init__(self, name, tags, an=False):
        self.name = name
        self.tags = tags
        self.tag_count = len(self.tags)
        self.guessed_tag_count = 0
        self.an = an
        if an:
            self.an_string = "n "
        else:
            self.an_string = " "

    async def process_guess(self, ctx, player, guess):
        if guess in self.tags:
            player.count += 1
            self.guessed_tag_count += 1
            self.tags.remove(guess)
            self.tag_count = len(self.tags)
            if self.tag_count == 0:
                remaining_str = "No {}s remaining!".format(self.name)
            elif self.tag_count == 1:
                remaining_str = "One {} remaining!".format(self.name)
            else:
                remaining_str = "{} {}s remaining!".format(self.tag_count, self.name)
            await ctx.send("You correctly guessed a{}{}! +1 point! {}".format(self.an_string, self.name, remaining_str))
            return True
        else:
            return False


class Derpi:
    """Derpibooru-related things."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['derpibooruuserswhatdotheytagdotheytagthingsletsfindout'])
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def guess(self, ctx, *args):
        """
        Derpibooru users. What do they tag? Do they tag things? Let's find out.

        A tag guessing game for derpibooru. Rules can be found here:
        https://sta.sh/01i7o1l7kvwz
        """

        ### CONSTANTS ###
        MAX_WRONG_GUESSES = 3
        MIN_SIMILARITY = 0.7
        TIMEOUT = 60
        #################

        if args:
            try:
                # check if first argument is a member
                converter = commands.MemberConverter()
                opponent = await converter.convert(ctx, args[0])
                user_query = list(args[1:])
                multiplayer = True
            except commands.BadArgument:
                opponent = ""
                user_query = list(args)
                multiplayer = False
        else:
            user_query = []
            multiplayer = False

        # separating singleplayer and multiplayer
        if multiplayer:

            challenger = ctx.author

            msg = await ctx.send("{0.mention}! You've been challenged to a derpibooru guessing game by {1.mention}! Do you accept?".format(opponent, challenger))
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            def check(reaction, user):
                return user == opponent and str(reaction.emoji) in ("✅", "❌") and reaction.message.id == msg.id
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=TIMEOUT)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. Exiting.")
                return

            if reaction.emoji == "❌":
                await ctx.send("Challenge denied. Exiting.")
                await msg.remove_reaction("✅", ctx.me)
                return
            else:
                await msg.remove_reaction("❌", ctx.me)
                await ctx.send("{} accepts!".format(opponent.display_name))


            player1 = Player(challenger)
            player2 = Player(opponent)

            # determine random starting player
            if random.randint(0, 1):
                active_player = player1
                inactive_player = player2
            else:
                active_player = player2
                inactive_player = player1

            await ctx.send("{} begins!".format(active_player.user.mention))

        else:
            active_player = Player(ctx.author)
            await ctx.send("Starting singleplayer game for {}!".format(active_player.user.mention))


        async with aiofiles.open("./data/aliases.json", loop=self.bot.loop) as f:
            aliases = json.loads(await f.read())
        if user_query:
            # replace tags with aliases where applicable
            for i in range(len(user_query)):
                user_query[i] = aliases.get(user_query[i], user_query[i])
            await ctx.send("The custom tags are: {}".format(", ".join(user_query)))
        # get random derpibooru image
        async with aiofiles.open("./data/derpibooru_query.json", loop=self.bot.loop) as f:
            query = json.loads(await f.read()) + user_query

        def search():
            return d.Search().query(*query).sort_by(d.sort.RANDOM).limit(1)

        search = next(await self.bot.loop.run_in_executor(None, search), None)
        if not search:
            await ctx.send("No image found!")
            return

        await ctx.send(search.full)
        if search.source_url:
            source = "<{}>".format(search.source_url)
        else:
            source = ""

        guessed_tags = []
        incorrect = []
        artists = Tag("artist tag", [tag for tag in search.tags if tag.startswith("artist:") and tag not in query], True)
        ocs = Tag("OC tag", [tag for tag in search.tags if tag.startswith("oc:") and tag not in query], True)
        tag_types = [artists, ocs]
        rating_tags = ["explicit", "grimdark", "grotesque", "questionable", "safe", "semi-grimdark", "suggestive"]
        tags = Tag("tag", [
            tag for tag in search.tags
            if not any(tag in tag_type.tags for tag_type in tag_types)
            and not tag in query
            and not tag.startswith("spoiler:")
            and not tag in rating_tags
        ])
        tag_count = tags.tag_count


        if artists.tag_count == 0:
            artist_string = ""
        elif artists.tag_count == 1:
            artist_string = " and an artist tag"
        else:
            artist_string = " and {} artist tags".format(artists.tag_count)

        if ocs.tag_count == 0:
            oc_string = ""
        elif ocs.tag_count == 1:
            oc_string = " It has one OC tag."
        else:
            oc_string = " It has {} OC tags.".format(ocs.tag_count)

        await ctx.send("This picture has {tags} tags{artist_str}.{oc_str}".format(tags=tags.tag_count, artist_str=artist_string, oc_str=oc_string))


        playing = True
        all_tags = False

        # check for similarity
        def compare(a, b):
            return difflib.SequenceMatcher(None, a, b).ratio()


        # basic turn structure
        async def turn(player):
            # returns True if the is cancelled
            await ctx.send("{0.user.display_name}! Guess a tag!".format(player))
            def check(msg):
                # parantheses to comment ingame
                return not re.fullmatch("\(.*\)", msg.content, re.IGNORECASE) and msg.channel == ctx.channel and msg.author == player.user
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=TIMEOUT)
            except asyncio.TimeoutError:
                await ctx.send("Timeout! This counts as a wrong guess.")
                player.wrong += 1
                if player.wrong >= MAX_WRONG_GUESSES:
                    await ctx.send("This is your 3rd wrong guess! You're out!")
                return False
            guess = msg.content.lower()
            alias = aliases.get(guess)
            if alias:
                await ctx.send("Replacing **{}** with alias **{}**.".format(guess, alias))
                guess = alias
            if guess == "stop!":
                await ctx.send("Cancelling the game.")
                await ctx.send("{}\n{}".format(search.url, source))
                # exit flag
                return True
            elif guess in guessed_tags:
                await ctx.send("You guessed that tag already!")
                return False
            elif guess in query:
                await ctx.send("You can't guess default tags!")
                return False
            elif guess in rating_tags:
                await ctx.send("You can't guess rating tags!")
                return False
            if await tags.process_guess(ctx, player, guess):
                guessed_tags.append(guess)
                return False
            # non-standard tags are separated for better scalability
            for tag_type in tag_types:
                if await tag_type.process_guess(ctx, player, guess):
                    guessed_tags.append(guess)
                    return False
            if any((compare(guess, x) >= MIN_SIMILARITY) for x in tags.tags):
                player.wrong +=1
                incorrect.append(guess)
                await ctx.send("Wrong, but you're close!")
                if player.wrong >= MAX_WRONG_GUESSES:
                    await ctx.send("This is your 3rd wrong guess. You're out!")
                return False
            else:
                player.wrong += 1
                incorrect.append(guess)
                await ctx.send("You guessed wrong.")
                if player.wrong >= MAX_WRONG_GUESSES:
                    await ctx.send("This is your 3rd wrong guess! You're out!")
                return False


        # game loop
        while playing:
            exit_flag = await turn(active_player)
            if exit_flag:
                # ending the program if the exit flag is received
                return
            if not tags.tags:
                all_tags = True
                playing = False
            # multiplayer lose condition
            elif multiplayer:
                if active_player.wrong >= MAX_WRONG_GUESSES and inactive_player.wrong >= MAX_WRONG_GUESSES:
                    playing = False
                elif inactive_player.wrong < MAX_WRONG_GUESSES:
                    active_player, inactive_player = inactive_player, active_player
            # singeplayer lose condition
            elif active_player.wrong >= MAX_WRONG_GUESSES:
                playing = False

        # multiplayer winner message
        if multiplayer:
            if player1.count == player2.count:
                winner = None
            elif player1.count > player2.count:
                winner = player1
            else:
                winner = player2

            if winner:
                winner_string = "{0.user.mention} wins!".format(winner)
            else:
                winner_string = "It's a tie!"


        if all_tags:
            unguessed = "Congratulations! You guessed all tags!"
        else:
            tag_ratio = round((tags.guessed_tag_count / tag_count) * 100)
            unguessed = "You guessed {}% of all tags! You didn't guess these tags: {}".format(tag_ratio, ", ".join(tags.tags))

        incorrect_str = "Incorrect guesses: {}.\nConsider adding missing tags!".format(", ".join(incorrect))

        # multiplayer and singleplayer score output
        if multiplayer:
            output = (

                "{unguessed}\n\n{incorrect}\n\n"
                "{p1.user.display_name} has earned {p1.count} points. {p2.user.display_name} has earned {p2.count} points.\n\n"
                "{winner_string}\n\n{url}\n{source}".format(
                    unguessed=unguessed,
                    incorrect=incorrect_str,
                    p1=player1,
                    p2=player2,
                    winner_string=winner_string,
                    url=search.url,
                    source=source
                )

            )
        else:
            output = (
                "{unguessed}\n\n{incorrect}\n\n"
                "You earned {p.count} points!\n\n"
                "{url}\n{source}".format(
                    unguessed=unguessed,
                    incorrect=incorrect_str,
                    p=active_player,
                    url=search.url,
                    source=source
                )
            )

        await ctx.send(output)


    @commands.group(hidden=True)
    async def alias(self, ctx):
        """ alias stuff """
        if ctx.invoked_subcommand is None:
            await ctx.send("The subcommands are add, check, and reverse.")


    @alias.command(aliases=["a"])
    @commands.is_owner()
    async def add(self, ctx):
        """
        Adds aliases. `!help alias add` for usage info.

        Usage:
        &alias add tag aliased_to
        """
        async with aiofiles.open("./data/aliases.json", loop=self.bot.loop) as f:
            aliases = json.loads(await f.read())

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        await ctx.send("Please name the tag you want to alias **to**.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            await ctx.send("Timeout. Exiting.")
            return
        target_tag = msg.content.lower()

        await ctx.send("Please name the tag or tags you want to alias **from**, separated by commas.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            await ctx.send("Timeout. Exiting.")
            return
        aliased_by = [tag.strip() for tag in msg.content.lower().split(",")]

        for tag in aliased_by:
            await ctx.send(tag)
            aliases.update([(tag, target_tag)])

        async with aiofiles.open("./data/aliases.json", mode="w", loop=self.bot.loop) as f:
            await f.write(json.dumps(aliases))

        await ctx.send("Added {} -> {} to aliases.".format(", ".join(aliased_by), target_tag))


    @alias.command(aliases=["rm"])
    @commands.is_owner()
    async def remove(self, ctx, *, tag):
        """Removes a tag from the alias database."""
        async with aiofiles.open("./data/aliases.json", loop=self.bot.loop) as f:
            aliases = json.loads(await f.read())

        target_tag = aliases.pop(tag, None)

        if not target_tag:
            await ctx.send("{} is not in the alias database.".format(tag))
            return

        async with aiofiles.open("./data/aliases.json", mode="w", loop=self.bot.loop) as f:
            await f.write(json.dumps(aliases))

        await ctx.send("Removed {} -> {} from the database.".format(tag, target_tag))


    @alias.command(aliases=["c"])
    async def check(self, ctx, *, tag):
        """Returns a tag's aliases, if any."""

        async with aiofiles.open("./data/aliases.json", loop=self.bot.loop) as f:
            aliases = json.loads(await f.read())

        aliased_to = aliases.get(tag)

        if aliased_to:
            await ctx.send("{} -> {}".format(tag, aliased_to))
        else:
            aliased_by = [_tag for _tag, alias in aliases.items() if alias == tag]
            if aliased_by:
                await ctx.send("{} <- {}".format(tag, ", ".join(aliased_by)))
            else:
                await ctx.send("No alias for {} found.".format(tag))

def setup(bot):
    bot.add_cog(Derpi(bot))
