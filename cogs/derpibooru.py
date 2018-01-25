import asyncio
import difflib
import json
import random
import re

import discord
from discord.ext import commands
import derpibooru as d

import checks

class Player:
    """Player class for the Derpibooru Game."""

    def __init__(self, user):
        self.user = user
        self.count = 0
        self.wrong = 0

class Derpibooru:
    """Derpibooru-related things."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['derpibooruuserswhatdotheytagdotheytagthingsletsfindout'], pass_context=True)
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def guess(self, ctx, opponent: discord.Member=None):
        """
        Derpibooru users. What do they tag? Do they tag things? Let's find out.

        A tag guessing game for derpibooru. Rules can be found here:
        https://sta.sh/01i7o1l7kvwz
        """

        # determining game mode
        if opponent:
            multiplayer = True
        else:
            multiplayer = False

        # check for similarity
        def compare(a, b):
            return difflib.SequenceMatcher(None, a, b).ratio()

        # basic turn structure
        async def turn(player):
            await self.bot.say("{0.user.display_name}! Guess a tag!".format(player))
            msg = await self.bot.wait_for_message(timeout=60, check=check, channel=channel, author=player.user)
            if not msg:
                await self.bot.say("Timeout! This counts as a wrong guess.")
                player.wrong += 1
                if player.wrong >= 3:
                    await self.bot.say("This is your 3rd wrong guess! You're out!")
                return
            guess = msg.content.lower()
            if guess == "stop!":
                await self.bot.say("Cancelling the game.")
                await self.bot.say(search.url)
                # exit signal
                return True
            elif guess in guessed_tags or guess in guessed_artists:
                await self.bot.say("You guessed that tag already!")
                return
            elif guess in query:
                await self.bot.say("You can't guess default tags!")
            elif guess in artist_tags:
                player.count += 1
                guessed_artists.append(guess)
                artist_tags.remove(guess)
                artist_count = len(artist_tags)
                if artist_count == 0:
                    artist_str = "No artist tags remaining."
                elif artist_count == 1:
                    artist_str = "One artist tag remaining."
                else:
                    artist_str = "{} artist tags remaining.".format(artist_count)
                await self.bot.say("You correctly guessed an artist tag! +1 point! {}".format(artist_str))
            elif guess in search.tags:
                player.count += 1
                guessed_tags.append(guess)
                remaining_tags.remove(guess)
                remaining = len(remaining_tags)
                if remaining == 0:
                    remaining_str = "No tags remaining!"
                elif remaining == 1:
                    remaining_str = "One tag remaining!"
                else:
                    remaining_str = "{} tags remaining!".format(remaining)
                await self.bot.say("You correctly guessed a tag! +1 point! {}".format(remaining_str))
                return
            elif any((compare(guess, x) >= 0.7) for x in remaining_tags):
                player.wrong +=1
                await self.bot.say("Wrong, but you're close!")
                if player.wrong >= 3:
                    await self.bot.say("This is your 3rd wrong guess. You're out!")
                return
            else:
                player.wrong += 1
                await self.bot.say("You guessed wrong.")
                if player.wrong >= 3:
                    await self.bot.say("This is your 3rd wrong guess! You're out!")
                return

        # parantheses to comment ingame
        def check(msg):
            return not re.fullmatch("\(.*\)", msg.content, re.IGNORECASE)

        channel = ctx.message.channel

        # separating singleplayer and multiplayer
        if multiplayer:

            challenger = ctx.message.author

            await self.bot.say("{0.mention}! You've been challenged to a derpibooru guessing game by {1.mention}! Do you accept?".format(opponent, challenger))
            def challenge_check(msg):
                return re.fullmatch("(y(es)?|n(o)?)", msg.content, re.IGNORECASE)
            msg = await self.bot.wait_for_message(timeout=60, check=challenge_check, channel=channel, author=opponent)
            if msg and re.fullmatch("y(es)?", msg.content, re.IGNORECASE):
                await self.bot.say("{} accepts!".format(opponent.display_name))
            elif not msg:
                await self.bot.say("Timeout. Exiting.")
                return
            else:
                await self.bot.say("Challenge denied. Exiting.")
                return

            player1 = Player(challenger)
            player2 = Player(opponent)

            # determine random starting player
            if random.randint(0, 1):
                active_player = player1
                inactive_player = player2
            else:
                active_player = player2
                inactive_player = player1

            await self.bot.say("{} begins!".format(active_player.user.mention))

        else:
            active_player = Player(ctx.message.author)
            await self.bot.say("Starting singleplayer game for {}!".format(active_player.user.mention))

        # get random derpibooru image
        with open("cogs/derpibooru_query.json") as f:
            query = json.load(f)

        search = next(d.Search().query(*query).sort_by(d.sort.RANDOM).limit(1))
        await self.bot.say(search.full)

        guessed_tags = []
        guessed_artists = []
        artist_tags = [tag for tag in search.tags if tag.startswith('artist:')]
        artist_count = len(artist_tags)
        remaining_tags = [tag for tag in search.tags if tag not in artist_tags and tag != 'safe']
        tag_count = len(remaining_tags)

        if artist_count == 0:
            await self.bot.say("This picture has {} tags and no artist tag.".format(tag_count))
        elif artist_count == 1:
            await self.bot.say("This picture has {} tags and an artist tag.".format(tag_count))
        else:
            await self.bot.say("This picture has {} tags and {} artist tags.".format(tag_count, artist_count))


        playing = True
        all_tags = False

        # game loop
        while playing:
            signal = await turn(active_player)
            # checking for exit signal
            if signal:
                return
            if not remaining_tags:
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
            tag_ratio = round((len(guessed_tags) / tag_count) * 100)
            unguessed = "You guessed {}% of all tags! You didn't guess these tags: {}".format(tag_ratio, ", ".join(remaining_tags))

        # multiplayer and singleplayer score output
        if multiplayer:
            output = "{0}\n\n{1.user.display_name} has earned {1.count} points. {2.user.display_name} has earned {2.count} points.\n\n{3}\n\n{4}".format(unguessed, player1, player2, winner_string, search.url)
        else:
            output = "{0}\n\nYou earned {1.count} points!\n\n{2}".format(unguessed, active_player, search.url)

        await self.bot.say(output)

def setup(bot):
    bot.add_cog(Derpibooru(bot))
