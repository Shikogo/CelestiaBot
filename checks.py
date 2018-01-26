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

owner = config["Authentication"]["owner"]
mod_roles = [x.strip() for x in config['Authentication']['mod_roles'].split(",")]
testserver_id = config['Servers']['testserver_id']

# Check functions to check for permissions
def is_me_check(ctx):
    return ctx.message.author.id == owner

def is_me():
    return commands.check(is_me_check)


def is_me_or_mod_check(ctx):
    if is_me_check(ctx):
        return True
    else:
        return discord.utils.find(lambda x: x.name in mod_roles, ctx.message.author.roles)

def is_me_or_mod():
    return commands.check(is_me_or_mod_check)


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
