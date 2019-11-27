'''
MIT License

Copyright (c) 2017-2018 Cree-Py

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import discord
import os
import io
import traceback
import textwrap
import inspect
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import redirect_stdout
from discord.ext import commands
import json
import subprocess
import asyncio
from ext.paginator import PaginatorSession


# def load_json(path, key):
#     with open(f'./data/{path}') as f:
#         config = json.load(f)
#     return config.get(key)


async def get_pre(bot, message):
    '''Gets the prefix for the guild'''
    try:
        result = await bot.db.config.find_one({'_id': str(message.guild.id)})
    except AttributeError:
        return '-'
    if not result or not result.get('prefix'):
        return '-'
    return result

bot = commands.Bot(command_prefix=".")
# with open('./data/auths.json') as f:
#     bot.auth = json.load(f)




bot.remove_command('help')
version = "v2.0.0"

@bot.command(name="load", discription="Loads a cog", hidden=True)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send('Successfully loaded')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(f"with {len(bot.guilds)} servers | .help | {version}"), afk=True)



    print('Bot is Online.')


@bot.command()
async def help(ctx):
	embed = discord.Embed(color=discord.Color.dark_teal())
	embed.add_field(name="Mathematics Commands", value="*add | subtract | multiply | power |divide*", inline=True)
	embed.add_field(name="Fun Commands", value="*slap | boxsim*", inline=True)
	embed.add_field(name="Search Commands", value="*img |  wiki*", inline=True)
	embed.add_field(name="Pokemon Commands", value="*pokerandom | pokeinfo | poketype*", inline=True)
	embed.add_field(name="Fun Commands I", value="*say | kill | cry | bully | smile | stare |asktrump | fuck | angry | cuddle | poke | pikachu | pat | drink | kiss| hug*", inline=True)
	embed.add_field(name="Action Commands", value="*ban | hackban | unban| kick | purge | mute | unmute | softban*", inline=True)
	await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    '''Pong! Get the bot's response time'''
    em = discord.Embed(color=discord.Color.green())
    em.title = "pong"
    em.description = f'{bot.latency * 1000} ms'
    await ctx.send(embed=em)


@bot.command(name='bot')
async def _bot(ctx):
    '''Shows info about bot'''
    em = discord.Embed(color=discord.Color.green())
    em.title = 'Bot Info'
    em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    try:
        em.description = bot.psa + '\n[Support Server](https://discord.gg/RzsYQ9f)'
    except AttributeError:
        em.description = 'A multipurpose bot made by Bushidoe'
    em.add_field(name="Servers", value=len(bot.guilds))
    em.add_field(name="Online Users", value=str(len({m.id for m in bot.get_all_members() if m.status is not discord.Status.offline})))
    em.add_field(name='Total Users', value=len(bot.users))
    em.add_field(name='Channels', value=f"{sum(1 for g in bot.guilds for _ in g.channels)}")
    em.add_field(name="Library", value=f"discord.py")
    em.add_field(name="Bot Latency", value=f"{bot.ws.latency * 1000:.0f} ms")

    em.set_footer(text="P1 bot | Powered by discord.py")
    await ctx.send(embed=em)



# if __name__ == "main":
#     print('Online.')
# else:
#     print('Fluffy coochie!')

if __name__ == '__main__':
    # bot.run(load_json('token.json', 'TOKEN'))
    # print('Bot is online.')
    bot.run(os.getenv('token'))
