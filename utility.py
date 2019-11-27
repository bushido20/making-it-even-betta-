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
import random
from discord.ext import commands
import urbandictionary as ud
import datetime
import pytz
import wikipedia
import inspect
from ext import utils


class Utility(commands.Cog):
    '''Useful and utility commands.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='presence', hidden=True)
    async def _presence(self, ctx, type=None, *, name=None):
        '''Change the bot's presence'''
        if type is None:
            await ctx.send(f'Usage: `{ctx.prefix}presence [game/stream/watch/listen] [message]`')
        else:
            if type.lower() == 'stream':
                await self.bot.change_presence(game=discord.Game(name=activity, type=1, url='https://www.twitch.tv/a'), status='online')
                await ctx.send(f'Set presence to. `Streaming {game}`')
            elif type.lower() == 'game':
                game = discord.Game(name)
                await self.bot.change_presence(activity=discord.Game(name=name))
                await ctx.send(f'Set presence to `Playing {game}`')
            elif type.lower() == 'watch':
                game = discord.Game(name)
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=name))
                await ctx.send(f'Set presence to `Watching {game}`')
            elif type.lower() == 'listen':
                game = discord.Game(name)
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=name))
                await ctx.send(f'Set presence to `Listening to {game}`')
            elif type.lower() == 'clear':
                await self.bot.change_presence(status=discord.Status.online, activity=None)
                await ctx.send('Cleared Presence')
            else:
                await ctx.send('Usage: `.presence [game/stream/watch/listen] [message]`')

    @commands.command()
    @utils.developer()
    async def source(self, ctx, command):
        '''Get the source code for any command.'''
        source = inspect.getsource(self.bot.get_command(command).callback)
        if not source:
            return await ctx.send(f'{command} is not a valid command.')
        try:
            await ctx.send(f'```py\n{source}\n```')
        except:
            paginated_text = utils.paginate(source)
            for page in paginated_text:
                if page == paginated_text[-1]:
                    await ctx.send(f'```py\n{page}\n```')
                    break
                await ctx.send(f'```py\n{page}\n```')

    @commands.command()
    async def embedsay(self, ctx, *, body: str):
        '''Send a simple embed'''
        em = discord.Embed(description=body, color=utils.random_color())
        await ctx.send(embed=em)

    @commands.command()
    async def tinyurl(self, ctx, *, link: str):
        '''Makes a link shorter using the tinyurl api'''
        await ctx.message.delete()
        url = 'http://tinyurl.com/api-create.php?url=' + link
        async with self.bot.session.get(url) as resp:
            new = await resp.text()
        emb = discord.Embed(color=random_color())
        emb.add_field(name="Original Link", value=link, inline=False)
        emb.add_field(name="Shortened Link", value=new, inline=False)
        emb.set_footer(text='Powered by tinyurl.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
        await ctx.send(embed=emb)

    @commands.command()
    async def hastebin(self, ctx, *, code):
        '''Hastebin-ify your code!'''
        code = utils.cleanup_code(code)
        async with self.bot.session.post("https://hastebin.com/documents", data=code) as resp:
            data = await resp.json()
            key = data['key']
        await ctx.send(f"Hastebin-ified! <https://hastebin.com/{key}.py>")

    @commands.command()
    async def datetime(self, ctx, tz=None):
        """Get the current date and time for a time zone or UTC."""
        now = datetime.datetime.now(tz=pytz.UTC)
        all_tz = 'https://github.com/cree-py/RemixBot/blob/master/data/timezones.json'
        if tz:
            try:
                now = now.astimezone(pytz.timezone(tz))
            except:
                em = discord.Embed(color=discord.Color.red())
                em.title = "Invalid timezone"
                em.description = f'Please take a look at the [list]({all_tz}) of timezones.'
                return await ctx.send(embed=em)
        await ctx.send(f'It is currently {now:%A, %B %d, %Y} at {now:%I:%M:%S %p}.')

    @commands.command(aliases=['urban'])
    async def ud(self, ctx, *, query):
        '''Search terms with urbandictionary.com'''
        em = discord.Embed(title=f'{query}', color=discord.Color.green())
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.set_footer(text='Powered by urbandictionary.com')
        defs = ud.define(query)
        try:
            res = defs[0]
        except IndexError:
            em.description = 'No results.'
            return await ctx.send(embed=em)
        em.description = f'**Definition:** {res.definition}\n**Usage:** {res.example}\n**Votes:** {res.upvotes}:thumbsup:{res.downvotes}:thumbsdown:'
        await ctx.send(embed=em)

    @commands.command(aliases=['wikipedia'])
    async def wiki(self, ctx, *, query):
        '''Search up something on wikipedia'''
        em = discord.Embed(title=str(query))
        em.set_footer(text='Powered by wikipedia.org')
        try:
            result = wikipedia.summary(query)
            if len(result) > 2000:
                em.color = discord.Color.red()
                em.description = f"Result is too long. View the website [here](https://wikipedia.org/wiki/{query.replace(' ', '_')}), or just google the subject."
                return await ctx.send(embed=em)
            em.color = discord.Color.green()
            em.description = result
            await ctx.send(embed=em)
        except wikipedia.exceptions.DisambiguationError as e:
            em.color = discord.Color.red()
            options = '\n'.join(e.options)
            em.description = f"**Options:**\n\n{options}"
            await ctx.send(embed=em)
        except wikipedia.exceptions.PageError:
            em.color = discord.Color.red()
            em.description = 'Error: Page not found.'
            await ctx.send(embed=em)

    @commands.command()
    async def suggest(self, ctx, *, idea: str):
        """Suggest an idea. Your idea will be sent to the developer server."""
        suggest = self.bot.get_channel(384111952798154752)
        em = discord.Embed(color=discord.Color.green())
        em.title = f"{ctx.author} | User ID: {ctx.author.id}"
        em.description = idea
        em.set_footer(text=f"From {ctx.author.guild} | Server ID: {ctx.author.guild.id}", icon_url=ctx.guild.icon_url)
        await suggest.send(embed=em)
        await ctx.send("Your idea has been successfully sent to support server. Thank you!")

    @commands.group(invoke_without_command=True)
    async def isit(self, ctx):
        '''A command group to see the number of days until a holiday'''
        await ctx.send(f'`{ctx.prefix}isit halloween` Find the number of days until this spooky holiday!\n`{ctx.prefix}isit christmas` Are you naughty or nice?\n`{ctx.prefix}isit newyear` When is next year coming already?')

    @isit.command()
    async def halloween(self, ctx):
        now = datetime.datetime.now()
        h = datetime.datetime(now.year, 10, 31)
        if now.month > 10:
            h = datetime.datetime(now.year + 1, 10, 31)
        until = h - now
        if now.month == 10 and now.day == 31:
            await ctx.send('It is Halloween! :jack_o_lantern: :ghost:')
        else:
            if until.days + 1 == 1:
                return await ctx.send('No, tomorrow is Halloween!')
            await ctx.send(f'No, there are {until.days + 1} more days until Halloween.')

    @isit.command()
    async def christmas(self, ctx):
        '''Is it Christmas?'''
        now = datetime.datetime.now()
        c = datetime.datetime(now.year, 12, 25)
        if now.month == 12 and now.day > 25:
            c = datetime.datetime((now.year + 1), 12, 25)
        until = c - now
        if now.month == 12 and now.day == 25:
            await ctx.send('Merry Christmas! :christmas_tree: :snowman2:')
        else:
            if until.days + 1 == 1:
                return await ctx.send('No, tomorrow is Christmas!')
            await ctx.send(f'No, there are {until.days + 1} more days until Christmas.')

    @isit.command()
    async def newyear(self, ctx):
        '''When is the new year?'''
        now = datetime.datetime.now()
        ny = datetime.datetime(now.year + 1, 1, 1)
        until = ny - now
        if now.month == 1 and now.day == 1:
            await ctx.send('It\'s New Years today! :tada:')
        else:
            if until.days + 1 == 1:
                return await ctx.send('No, tomorrow is New Year\'s Day!')
            await ctx.send(f'No, there are {until.days + 1} days left until New Year\'s Day.')

    @commands.group(invoke_without_command=True)
    async def math(self, ctx):
        '''A command group for math commands'''
        await ctx.send('Available commands:\n`add <a> <b>`\n`subtract <a> <b>`\n`multiply <a> <b>`\n`divide <a> <b>`\n`remainder <a> <b>`\n`power <a> <b>`\n`factorial <a>`')

    @math.command(aliases=['*', 'x'])
    async def multiply(self, ctx, a: int, b: int):
        '''Multiply two numbers'''
        em = discord.Embed(color=discord.Color.green())
        em.title = "Result"
        em.description = f'❓ Problem: `{a}*{b}`\n✅ Solution: `{a * b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['/', '÷'])
    async def divide(self, ctx, a: int, b: int):
        '''Divide a number by a number'''
        try:
            em = discord.Embed(color=discord.Color.green())
            em.title = "Result"
            em.description = f'❓ Problem: `{a}/{b}`\n✅ Solution: `{a / b}`'
            await ctx.send(embed=em)
        except ZeroDivisionError:
            em = discord.Embed(color=discord.Color.green())
            em.title = "Error"
            em.description = "You can't divide by zero"
            await ctx.send(embed=em)

    @math.command(aliases=['+'])
    async def add(self, ctx, a: int, b: int):
        '''Add a number to a number'''
        em = discord.Embed(color=discord.Color.green())
        em.title = "Result"
        em.description = f'❓ Problem: `{a}+{b}`\n✅ Solution: `{a + b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['-'])
    async def subtract(self, ctx, a: int, b: int):
        '''Substract two numbers'''
        em = discord.Embed(color=discord.Color.green())
        em.title = "Result"
        em.description = f'❓ Problem: `{a}-{b}`\n✅ Solution: `{a - b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['%'])
    async def remainder(self, ctx, a: int, b: int):
        '''Gets a remainder'''
        em = discord.Embed(color=discord.Color.green())
        em.title = "Result"
        em.description = f'❓ Problem: `{a}%{b}`\n✅ Solution: `{a % b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['^', '**'])
    async def power(self, ctx, a: int, b: int):
        '''Raise A to the power of B'''
        if a > 100 or b > 100:
            return await ctx.send("Numbers are too large.")
        em = discord.Embed(color=discord.Color.green())
        em.title = "Result"
        em.description = f'❓ Problem: `{a}^{b}`\n✅ Solution: `{a ** b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['!'])
    async def factorial(self, ctx, a: int):
        '''Factorial something'''
        if a > 813:
            await ctx.send("That number is too high to fit within the message limit for discord.")
        else:
            em = discord.Embed(color=discord.Color.green())
            em.title = "Result"
            result = 1
            problem = a
            while a > 0:
                result = result * a
                a = a - 1
            em.description = f'❓ Problem: `{problem}!`\n✅ Solution: `{result}`'
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Utility(bot))
