#!/usr/bin/env python3

import asyncio
import configparser
import logging
import random
import re
import uvloop

import discord
from discord.ext import commands

import checks
import patterns

# Loading up the config file.
config = configparser.ConfigParser()
config.read("config.ini")

#setting up logging
logging.basicConfig(
    filename = "celestia.log",
    level = logging.INFO,
    format = "{asctime}:{levelname}: {message}",
    style = "{")


prefix = [x.strip() for x in config['Bot']['prefix'].split(",")]
description = config['Bot']['description']
game = config['Bot']['game']
startup_extensions = [x.strip() for x in config['Bot']['cogs'].split(",")]

# setting the loop to uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

bot = commands.Bot(command_prefix=prefix, description=description)


@bot.event
async def on_ready():
    """Runs after the bot has successfully connected."""
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    bot.add_check(checks.is_not_blacklisted)
    await bot.change_presence(game=discord.Game(name=game))

    global pat
    pat = patterns.Patterns(bot.user.id)


    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
            print("Successfully loaded {}.".format(extension))
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load extension {}\n{}.".format(extension, exc))


@bot.event
async def on_command_error(ctx, error):
    """Runs if a bot command raises an error."""
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("Sorry, you are not allowed to use this command.")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("`{0}{1}` is not a valid command. Try `{0}help`.".format(ctx.prefix, ctx.invoked_with))
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("This command is on cooldown. You may use it again in {0}s.".format(round(error.retry_after, 1)))
    else:
        await ctx.send("```py\n{}: {}\n```".format(type(error).__name__, str(error)))
        raise error


@bot.event
async def on_message(message):
    """Various AI responses to things that users say."""
    if message.author.id not in checks.blacklist and not message.author.bot:
        if pat.hug.match(message.content):
            response = random.choice([
                "_hugs {}_",
                "_embraces {}_",
                "_gives {} a big wing hug_",
                "_squeezes {}_"
            ])
            await ai_response(message.channel, response.format(message.author.mention))
        elif pat.greet.fullmatch(message.content):
            response = random.choice([
                "[](/grinlestia) Hi, {}!",
                "[](/celestia) Hello, {}.",
                "[](/lcehappy) Hey there, {}."
            ])
            await ai_response(message.channel, response.format(message.author.mention))
        elif pat.morning.fullmatch(message.content):
            response = random.choice([
                "[](/grinlestia) A wonderful morning to you, {}!",
                "[](/celestia) Good morning, {}!"
            ])
            await ai_response(message.channel, response.format(message.author.mention))
        elif pat.bap.match(message.content):
            response = random.choice([
                "[](/celestiasad)",
                "[](/tiam04)"
            ])
            await ai_response(message.channel, response)
        elif pat.konami.search(message.content):
            await message.guild.me.edit(nick="LVL 100 SUPERPONY EX+")
            await message.channel.send("[](/octybelleintensifies)")
            await asyncio.sleep(15)
            await message.guild.me.edit(nick=None)
        elif pat.derpi.search(message.content):
            post_id_raw = pat.derpi.search(message.content).group().split("/")[-1]
            post_id = re.match("\d+", post_id_raw).group()
            await message.channel.send("<http://derpibooru.org/{}>".format(post_id))
        else:
            # starts processing of commands
            if message.content:
                # turn first word lower case
                msg = message.content.split(maxsplit=1)
                msg[0] = msg[0].lower()
                message.content = " ".join(msg)
            await bot.process_commands(message)


async def ai_response(channel, message, wait=1):
    async with channel.typing():
        await asyncio.sleep(wait)
        await channel.send(message)


@bot.command(hidden = True)
@commands.is_owner()
async def load(ctx, extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))


@bot.command(hidden = True)
@commands.is_owner()
async def unload(ctx, extension_name: str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await ctx.send("{} unloaded.".format(extension_name))


@bot.command(hidden = True)
@commands.is_owner()
async def reload(ctx, extension_name: str):
    """Reloads an extension."""
    await ctx.invoke(unload, extension_name)
    await ctx.invoke(load, extension_name)

if __name__ == "__main__":
    token = config['Authentication']['token']
    bot.run(token, bot=True)
