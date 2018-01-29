import asyncio
import difflib
import json
import random
import re

import discord
from discord.ext import commands
import derpibooru as d
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
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
        self.tag_count = len(self.tags)
        self.guessed_tag_count = 0

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
            await ctx.send("You correctly guessed a {}! +1 point! {}".format(self.name, remaining_str))
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
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("Timeout! This counts as a wrong guess.")
                player.wrong += 1
                if player.wrong >= 3:
                    await ctx.send("This is your 3rd wrong guess! You're out!")
                return False
            guess = msg.content.lower()
            if guess in aliases.keys():
                guess = aliases[guess]
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
            if await tags.process_guess(ctx, player, guess):
                guessed_tags.append(guess)
                return False
            # non-standard tags are separated for better scalability
            for tag_type in tag_types:
                if await tag_type.process_guess(ctx, player, guess):
                    guessed_tags.append(guess)
                    return False
            if any((compare(guess, x) >= 0.7) for x in tags.tags):
                player.wrong +=1
                await ctx.send("Wrong, but you're close!")
                if player.wrong >= 3:
                    await ctx.send("This is your 3rd wrong guess. You're out!")
                return False
            else:
                player.wrong += 1
                await ctx.send("You guessed wrong.")
                if player.wrong >= 3:
                    await ctx.send("This is your 3rd wrong guess! You're out!")
                return False


        # separating singleplayer and multiplayer
        if multiplayer:

            challenger = ctx.author

            await ctx.send("{0.mention}! You've been challenged to a derpibooru guessing game by {1.mention}! Do you accept?".format(opponent, challenger))
            def challenge_check(msg):
                return re.fullmatch("(y(es)?|no?)", msg.content, re.IGNORECASE) and msg.author == opponent and msg.channel == ctx.channel
            try:
                msg = await self.bot.wait_for("message", check=challenge_check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. Exiting.")
                return
            if re.fullmatch("no?", msg.content, re.IGNORECASE):
                await ctx.send("Challenge denied. Exiting.")
                return
            else:
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


        with open("./data/aliases.json") as f:
            aliases = json.load(f)
        if user_query:
            # replace aliased tags in the user query with their counterparts
            for i in range(len(user_query)):
                if user_query[i] in aliases.keys():
                    user_query[i] = aliases[user_query[i]]
            await ctx.send("The custom tags are: {}".format(", ".join(user_query)))
        # get random derpibooru image
        with open("./data/derpibooru_query.json") as f:
            query = json.load(f) + user_query

        try:
            search = next(d.Search().query(*query).sort_by(d.sort.RANDOM).limit(1))
        except StopIteration:
            await ctx.send("No image found!")
            return

        await ctx.send(search.full)
        if search.source_url:
            source = "<{}>".format(search.source_url)
        else:
            source = ""

        guessed_tags = []
        artists = Tag("artist tag", [tag for tag in search.tags if tag.startswith('artist:') and tag not in query])
        ocs = Tag("OC tag", [tag for tag in search.tags if tag.startswith("oc:") and tag not in query])
        tag_types = [artists, ocs]
        tags = Tag("tag", [tag for tag in search.tags if not any(tag in tag_type.tags for tag_type in tag_types) and not tag in query])
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
                if active_player.wrong >= 3 and inactive_player.wrong >= 3:
                    playing = False
                elif inactive_player.wrong < 3:
                    active_player, inactive_player = inactive_player, active_player
            # singeplayer lose condition
            elif active_player.wrong >= 3:
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

        # multiplayer and singleplayer score output
        if multiplayer:
            output = "{0}\n\n{1.user.display_name} has earned {1.count} points. {2.user.display_name} has earned {2.count} points.\n\n{3}\n\n{4}\n{5}".format(
                unguessed, player1, player2, winner_string, search.url, source
            )
        else:
            output = "{0}\n\nYou earned {1.count} points!\n\n{2}\n{3}".format(unguessed, active_player, search.url, source)

        await ctx.send(output)

def setup(bot):
    bot.add_cog(Derpi(bot))
