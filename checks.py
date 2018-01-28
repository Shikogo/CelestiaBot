import configparser
import json

import discord
from discord.ext import commands

class Blacklisted(commands.CommandError): pass

# blacklist
try:
    with open('blacklist.json') as f:
        blacklist = set(json.load(f))
except FileNotFoundError:
    blacklist = set()

config = configparser.ConfigParser()
config.read("config.ini")

mod_roles = [x.strip() for x in config['Authentication']['mod_roles'].split(",")]
testserver_id = int(config['Servers']['testserver_id'])

# Check functions to check for permissions


def is_mod():
    async def predicate(ctx):
        return await ctx.bot.is_owner(ctx.author) or any(role.name in mod_roles for role in ctx.author.roles)
    return commands.check(predicate)


def is_not_blacklisted(ctx):
    if ctx.message.author.id in blacklist:
        raise Blacklisted()
        return None
    else:
        return not ctx.message.author.bot


def is_testserver_check(ctx):
    return ctx.message.server.id == testserver_id

def is_testserver():
    return commands.check(is_testserver_check)
