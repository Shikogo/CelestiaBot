import asyncio
import random
import re

from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ext import commands

import checks


class Player:
    """ Player class for games and stuff """

    def __init__(self, user):
        self.user = user
        self.score = 0


class Fun:
    """Contains fun commands!!"""
    def __init__(self, bot):
        self.bot = bot
        self.praises = {
            re.compile("((the )?sun)|", re.IGNORECASE) : (
                "Praise the sun! [](/grinlestia)",
            ),
            re.compile("(princess )?((celes)?tia|sun ?(butt|horse|pon[ye])|cell?y|(the )princess of (the )suns?|you(rself)?|<@!?{0}>)".format(self.bot.user.id), re.IGNORECASE) : (
                "Why thank you! [](/celestiaglee)",
                "Aww, I like you too, {author.mention}! [](/celestlove)"
            ),
            re.compile("((princess )?((lu|woo)na|moonbutt)|your sister|<@!?175829806041006082>)", re.IGNORECASE) : (
                "[](/awelestia) Hey Princess Luna, you're up!",
                "But.. I want praise, too. [](/tiajealous)",
                "*hugs Luna [](/lunacelehug)*",
                "[](/pimpcess) Praise us!"
            ),
            re.compile("(the )?moon", re.IGNORECASE) : (
                "Praise celestial objects! [](/celestia)",
                "[](/celestiasup) The moon *does* have its uses...",
                "You praised the wrong one. [](/tiam16)",
                "That's... Luna's job. [](/tiam06)"
            ),
            re.compile("(((420 )?blaze )?it|420)", re.IGNORECASE) : (
                "[](/d15)",
                "[](/d04) 420"
            ),
            re.compile("((the )?sun queen|(#)?hysq|thunder ?(storm|rey)|rey|radiant resplendence)", re.IGNORECASE) : (
                "#HYSQ",
                "Hell yeah Sun Queen!"
            ),
            re.compile("((the )?apples|apple(jack| ?bloom)|(prince(ss)? )?big mac(intosh)?|(the )?apple family|e+yup|e+n+ope)", re.IGNORECASE) : (
                "[](/princessmac-r) Eeyup!",
            ),
            re.compile("(pok[eé]mon( go)?|mew)", re.IGNORECASE) : (
                "[](/mewlestia) Gotta catch 'em all!",
            ),
            re.compile("((copper ?|kitty)core( is cute(\+\+)?)?|chadwick|<@(!)?148092962214117376>)", re.IGNORECASE) : (
                "coppercore is cute++",
            )

        }

    @commands.command(aliases = ["praises"])
    async def praise(self, ctx, *, obj=""):
        """Praises things. Usually the sun."""

        if len(obj) > 50:
            await ctx.send("[](/properbudget) That's a bit long, don't you think?")
            return

        for key in self.praises:
            match = re.fullmatch(key, obj)
            if match:
                response = random.choice(self.praises[key])
                await ctx.send(response.format(author=ctx.author))
                return

        if re.fullmatch("({0.mention}|{0.display_name}|{0.name}|me|myself)".format(ctx.author),
                          obj, re.IGNORECASE):
            response = random.choice([
                "[](/celestiamad) You're praising yourself? Really?",
                "[](/lcewat) Praise {0.mention}, the most humble person in the universe.",
                "Praise you! [](/clop12)"
            ])
            await ctx.send(response.format(ctx.author))

        elif re.fullmatch("((queen )?(chrysalis|chryss(i(e)?|y))|changelings?|bug horses?|thorax|spectre)",
                          obj, re.IGNORECASE):
            await ctx.guild.me.edit(nick="Queen Chrysalis")
            await ctx.send("[](/queenlove)")
            await asyncio.sleep(60, loop=self.bot.loop)
            await ctx.guild.me.edit(nick=None)

        elif re.fullmatch("recursion", obj, re.IGNORECASE):
            for i in range(5):
                await ctx.send("&praise recursion")
                await asyncio.sleep(1, loop=self.bot.loop)
            await ctx.send("Oops. Sorry about that. [](/lcesurprised)")

        elif re.fullmatch("fl(a|e|i|o|u|ä|ü|ö|0){2,}f", obj, re.IGNORECASE):
            os = "o" * random.randint(2, 20)
            await ctx.send("[](/celsit) fl{0}f!".format(os))

        else:
            response = random.choice([
                # positive responses
                "[](/tianom) Heck yeah {obj}!",
                "[](/celestia) Praise {obj}!",
                "[](/celestiabarf) {obj_cap}...",
                "I *do* like {obj}... [](/celestibrows)",
                "[](/deepcelebounce) {obj_cap}! {obj_cap}! {obj_cap}!",
                "{obj}++",
                "Let's dance the {obj} dance! [](/celestiadansen)",
                "They just don't make {obj} like they used to anymore...",
                "{obj} is magic!",
                "[](/celoohshiny) Ooh, I could go for a {obj} right now.",
                "[](/tiam08) You can never have enough {obj}.",

                # negative responses
                "[](/celestiafrown) Why would you praise {obj}...?",
                "[](/celestlol) You praise {obj}?",
                "[](/tiano)",
                "[](/cod) {obj_cap}? Really?",
                "{obj_cap}? Eh, I'm gonna praise the sun instead. [](/celestfly)",
                "I'm not gonna stoop so low as to praise {obj}.\nLuna on the other hand... [](/implylestia)",
                "[](/tiam14) I'd rather not praise {obj} in front of everyone...",

                # jokes
                "```Error: praise_{obj} not found. [](/clearlestia)```",
                "{obj_cap}? Princess Luna is an *expert* about that.",
                "[](/crazylestia) {obj_cap} for the {obj} god!",
                "[](/celdevious) It's true, for only 99c a minute I will praise {obj} just for you...",
                "{obj_cap}? I don't even know what that is... [](/tiapoker)"
            ])
            await ctx.send(response.format(obj=obj, obj_cap=obj.capitalize()))


    @commands.command(aliases=["colour", "couleur", "farbe", "色"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def color(self, ctx, *, msg):
        """Produces colorful text!"""
        for member in ctx.message.mentions:
            msg = msg.replace("<@{}>".format(member.id), "@{}".format(member.display_name))
            msg = msg.replace("<@!{}>".format(member.id), "@{}".format(member.display_name))
        for channel in ctx.message.channel_mentions:
            msg = msg.replace("<#{}>".format(channel.id), "#{}".format(channel.name))

        choice = random.randint(1,100)
        if choice == 1:
            msg = "dickbutt"
        if choice >= 10:
            font = ImageFont.truetype("fonts/equestria.ttf", 40)
        else:
            font = ImageFont.truetype("fonts/comic.ttf", 40)
        img = Image.new("RGB", (1, 1)) #dummy image so textsize works
        draw = ImageDraw.Draw(img)

        text_w, text_h = draw.textsize(msg, font)

        if text_w <= 800 and text_h <= 200:
            img = Image.new("RGBA", (text_w+10, text_h+10), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            draw.text((5, 0), msg, (random.randint(10,255),random.randint(10,255),random.randint(10,255)), font)
            img.save("output.png", "png")
            await ctx.send(file=discord.File("output.png"))

        else:
            await ctx.send("Your text is too long.")


    @commands.command(aliases=["magiceight", "magic8ball", "m8"])
    async def magic8(self, ctx):
        """
        It's a magic 8 ball!

        Responses are based on the actual Magic 8 Ball product.
        """
        answer = random.choice([
            # positive responses
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes, definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",

            # neutral responses
            "Reply hazy try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",

            # negative responses
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ])
        await ctx.send('*{}*'.format(answer))


    @commands.command(pass_context=True)
    async def dgmp(self, ctx, opponent: discord.Member=None):
        """
        Dice Game Multiplayer (DGMP)
        Challenge a friend to a game of dice!

        A player rolls a d6 and adds the rolls. If they roll a 1, they lose all
        points they gained this turn and pass the turn. A player may pass their
        turn after each roll to save their score.
        First to get to 50 wins! But be careful. If you get more than 50 points,
        you also lose all points you gained that turn, and pass the turn!
        """

        # if ctx.message.author == opponent:
        #     await self.bot.say("You can't challenge yourself, dummy!")
        #     return

        if not opponent:
            await ctx.send("You can't play DGMP alone.")
            return

        channel = ctx.channel
        challenger = ctx.author

        def check(msg):
            return re.fullmatch("(y(es)?|n(o)?)", msg.content, re.IGNORECASE) and msg.author == opponent and msg.channel == channel

        await ctx.send("{0.mention}! You were challenged to a dice game by {1.mention}! Do you accept?".format(opponent, challenger))
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Aborting match.")
            return
        if re.fullmatch("n(o)?", msg.content, re.IGNORECASE):
            await ctx.send("[](/sadtia) https://www.youtube.com/watch?v=-EQ6eHeBrhM")
            return
        else:
            await ctx.send("{0.display_name} has accepted! A random player will start the match!\n\n".format(opponent))
            await asyncio.sleep(2, loop=self.bot.loop)

        player1 = Player(challenger)
        player2 = Player(opponent)

        if random.randint(0, 1):
            active_player = player1
            inactive_player = player2
        else:
            active_player = player2
            inactive_player = player1


        async def turn(player):
            """ This is run for each turn. """
            await ctx.send("{0.user.display_name}'s turn!".format(player))
            playing = True
            temp_score = 0
            temp_total = player.score
            def check(msg):
                return re.fullmatch("(y(es)?|no?|stop!)", msg.content, re.IGNORECASE) and msg.author == player.user and msg.channel == channel

            while playing:
                roll = random.randint(1,6)
                if roll == 1:
                    await ctx.send("You rolled a **1**... You lose **{temp}** points. "
                                       "You return to your **{total}** point total.\n"
                                       "Your turn is over!".format(temp=temp_score, total=player.score))
                                       # game continues
                    return 0
                else:
                    temp_score += roll
                    temp_total += roll
                    if temp_total >= 50:
                        # active player wins!
                        await ctx.send("You rolled a **{}**!".format(roll))
                        player.score = temp_total
                        return 1
                    else:
                        await ctx.send("You rolled a **{roll}**! You have accumulated **{temp}** points this turn. "
                                           "Your current total is **{temp_total}**.\n\n"
                                           "Roll again?".format(roll=roll, temp=temp_score, temp_total=temp_total))
                        try:
                            msg = await self.bot.wait_for("message", check=check, timeout=60)
                        except asyncio.TimeoutError:
                            await ctx.send("Timeout. Ending the match.")
                            return -1
                        if re.fullmatch("stop!", msg.content, re.IGNORECASE):
                            ctx.send("Ending the match.")
                            return -1
                        elif re.fullmatch("no?", msg.content, re.IGNORECASE):
                            player.score = temp_total
                            await ctx.send("{player.user.display_name} passes the turn with **{temp_total}** points.".format(player=player, temp_total=temp_total))
                            # game continues
                            return 0

        # game loop
        while True:
            turn_result = await turn(active_player)

            if turn_result == -1:
                # match ended, message sent in the turn fuction.
                return
            elif turn_result == 1:
                await ctx.send("{0.user.display_name} wins the match with **{0.score}** points!! Congratulations!".format(active_player))
                return
            else:
                active_player, inactive_player = inactive_player, active_player


def setup(bot):
    bot.add_cog(Fun(bot))
