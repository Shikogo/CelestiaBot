#!/usr/bin/env python

import asyncio
import configparser
import logging
import random
import re

import discord
from discord.ext import commands

import checks

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

bot = commands.Bot(command_prefix=prefix, description=description)

startup_extensions = [x.strip() for x in config['Bot']['cogs'].split(",")]

@bot.event
async def on_ready():
    """Runs after the bot has successfully connected."""
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    bot.add_check(checks.is_not_blacklisted)
    await bot.change_presence(game=discord.Game(name=game))

    if bot.servers:
        print("Connected to: {}".format(", ".join([server.name for server in bot.servers])))
    else:
        print("No servers connected.")

    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
            print("Successfully loaded {}.".format(extension))
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load extension{}\n{}.".format(extension, exc))


@bot.event
async def on_command_error(error, ctx):
    """Runs if a bot command raises an error."""
    if isinstance(error, commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel,
            "Sorry, you are not allowed to use this command.")
    elif isinstance(error, commands.errors.CommandNotFound):
        await bot.send_message(ctx.message.channel,
            "`{0}{1}` is not a valid command. Try `{0}help`.".format(ctx.prefix, ctx.invoked_with))
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await bot.send_message(ctx.message.channel,
            "This command is on cooldown. You may use it again in {0}s.".format(round(error.retry_after, 1)))
    else:
        await bot.send_message(ctx.message.channel,
            "```py\n{}: {}\n```".format(type(error).__name__, str(error)))
        raise error




# Regex for AI
re_celestia = "(princess )?((celes)?tia|sun ?(butt|horse|pon[ye])|cell?y|(the )princess of (the )suns?|<@!?197809480686239744>)"
re_hug = re.compile("[_\*](hug(gle)?s|glomps|snug(gle)?s( with)?|squeezes) ({}|every(one|pony))".format(re_celestia), re.IGNORECASE)
re_greet = re.compile("(hi|hello|hey|(good )?afternoon) (every(one|pony)|(y'?)?all|friends|folks|guys|{})!*".format(re_celestia), re.IGNORECASE)
re_morning = re.compile("(good |')?mornin(g|')? (every(one|pony)|(y'?)?all|friends|folks|guys|{})!*".format(re_celestia), re.IGNORECASE)
re_bap = re.compile("(_(baps|smacks|hits|slaps)|bad) {}".format(re_celestia), re.IGNORECASE)
re_konami = re.compile(r"((up|🔼|⬆|\^)\s?){2}((down|🔽|⬇|v)\s?){2}((left\s?right|⬅\s?➡|◀\s?▶|<\s?>)\s?){2}(B|🅱)\s?(A|🅰)", re.IGNORECASE)
re_derpi = re.compile(r"derpicdn\.net/img/(view/)?\d+/\d+/\d+/\d+")
# re_give = re.compile("[_\*]gives {} (a|the)?", re.IGNORECASE)


@bot.event
async def on_message(message):
    """Various AI responses to things that users say."""
    if message.author.id not in checks.blacklist and not message.author.bot:
        if re_hug.match(message.content):
            response = random.choice([
                "_hugs {}_",
                "_embraces {}_",
                "_gives {} a big wing hug_",
                "_squeezes {}_"
            ])
            await ai_response(message.channel, response.format(message.author.mention))
        elif re_greet.fullmatch(message.content):
            response = random.choice([
                "[](/grinlestia) Hi, {}!",
                "[](/celestia) Hello, {}.",
                "[](/lcehappy) Hey there, {}."
            ])
            await ai_response(message.channel, response.format(message.author.mention))
        elif re_morning.fullmatch(message.content):
            response = random.choice([
                "[](/grinlestia) A wonderful morning to you, {}!",
                "[](/celestia) Good morning, {}!"
            ])
            await ai_response(message.channel, response.format(message.author.mention))
        elif re_bap.match(message.content):
            response = random.choice([
                "[](/celestiasad)",
                "[](/tiam04)"
            ])
            await ai_response(message.channel, response)
        elif re_konami.search(message.content):
            await bot.change_nickname(message.server.me, "LVL 100 SUPERPONY EX+")
            await bot.send_message(message.channel, "[](/octybelleintensifies)")
            await asyncio.sleep(15)
            await bot.change_nickname(message.server.me, None)
        elif re_derpi.search(message.content):
            post_id_raw = re_derpi.search(message.content).group().split("/")[-1]
            post_id = re.match("\d+", post_id_raw).group()
            await bot.send_message(message.channel, "<http://derpibooru.org/{}>".format(post_id))
        else:
            # starts processing of commands
            if message.content:
                # turn first word lower case
                msg = message.content.split(maxsplit=1)
                msg[0] = msg[0].lower()
                message.content = " ".join(msg)
            await bot.process_commands(message)


async def ai_response(channel, message, wait=1):
    await bot.send_typing(channel)
    await asyncio.sleep(wait)
    await bot.send_message(channel, message)


@bot.command(hidden = True)
@checks.is_me()
async def load(extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))


@bot.command(hidden = True)
@checks.is_me()
async def unload(extension_name: str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@bot.command(hidden = True, pass_context=True)
@checks.is_me()
async def reload(ctx, extension_name: str):
    """Reloads an extension."""
    await ctx.invoke(unload, extension_name)
    await ctx.invoke(load, extension_name)

if __name__ == "__main__":
    token = config['Authentication']['token']
    bot.run(token, bot=True)
