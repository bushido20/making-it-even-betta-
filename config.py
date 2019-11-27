'''
MIT License

Copyright (c) 2017-2018 Cree-py

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
from discord.ext import commands
import datetime


class Config(commands.Cog):
    '''Customize your server with these config commands.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, *, pre):
        '''Set a custom prefix for the guild.'''
        result = await self.bot.db.config.find_one({'_id': str(ctx.guild.id)})
        if not result:
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': {'_id': str(ctx.guild.id), 'prefix': str(pre)}})
            return ctx.send(f'The guild prefix has been set to `{pre}` Use `{pre}prefix <prefix>` to change it again.')
        result['prefix'] = str(pre)
        await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': result})
        await ctx.send(f'The guild prefix has been set to `{pre}` Use `{pre}prefix <prefix>` to change it again.')

    @commands.command(aliases=['setwelcome', 'welcomemsg', 'joinmessage', 'welcomeset'], no_pm=True)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx, type):
        '''Enable or disable a welcome message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        config = await self.bot.db.config.find_one({'_id': str(ctx.guild.id)})
        if not config:
            config = {'_id': str(ctx.guild.id), 'welctype': False}

        if type.lower() in ('n', 'no', 'disabled', 'disable', 'off'):
            config['welctype'] = False
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': config})
            await ctx.send('Welcome messages disabled for this guild.')
        else:
            config['welctype'] = True
            await ctx.send('Which channel do you want the welcome messages to be set to? Use a channel mention.')
            channel = await self.bot.wait_for('message', check=pred, timeout=60.0)
            id = channel.content.strip('<#').strip('>')
            if id == channel.content:
                return await ctx.send('Please mention a channel.')
            config['welcchannel'] = str(id)
            await ctx.send('What do you want the message to be?\nUsage:```\n{mention}: Mentions the joining user.\n{name}: Replaces this with the user\'s name.\n{server}: Server name.\n{membercount}: Returns the number of members in the guild.\n```')
            msg = await self.bot.wait_for('message', check=pred, timeout=60.0)
            config['welc'] = str(msg.content).replace('"', '\"')
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': config})
            await ctx.send('Your welcome message has been successfully set.')

    @commands.command(aliases=['setleave', 'leavemsg', 'leavemessage', 'leaveset'], no_pm=True)
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        config = await self.bot.db.config.find_one({'_id': str(ctx.guild.id)})
        if not config:
            config = {'_id': str(ctx.guild.id), 'leavetype': False}

        if type.lower() in ('n', 'no', 'disabled', 'disable', 'off'):
            config['leavetype'] = False
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': config})
            await ctx.send('Leave messages disabled for this guild.')
        else:
            config['leavetype'] = True
            await ctx.send('Which channel do you want the leave messages to be set to? Use a channel mention.')
            channel = await self.bot.wait_for('message', check=pred, timeout=60.0)
            id = channel.content.strip('<#').strip('>')
            if id == channel.content:
                return await ctx.send('Please mention a channel.')
            config['leavechannel'] = str(id)
            await ctx.send('What do you want the message to be?\nUsage:```\n{name}: Replaces this with the user\'s name.\n{server}: Server name.\n{membercount}: Returns the number of members in the guild.\n```')
            msg = await self.bot.wait_for('message', check=pred, timeout=60.0)
            config['leave'] = str(msg.content).replace('"', '\"')
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': config})
            await ctx.send('Your leave message has been successfully set.')

    @commands.command(aliases=['mod-log'])
    @commands.has_permissions(view_audit_log=True)
    async def modlog(self, ctx, type):
        '''Toggle mod-logs for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        config = await self.bot.db.config.find_one({'_id': str(ctx.guild.id)})
        if not config:
            config = {'_id': str(ctx.guild.id), 'logtype': False}

        if type.lower() in ('n', 'no', 'disabled', 'disable', 'off'):
            config['logtype'] = False
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': config})
            await ctx.send('Mod-logs are disabled for this guild.')
        else:
            config['logtype'] = True
            await ctx.send('Which channel do you want the events to be logged in? Use a channel mention.')
            channel = await self.bot.wait_for('message', check=pred, timeout=60.0)
            id = channel.content.strip('<#').strip('>')
            if id == channel.content:
                return await ctx.send('Please mention a channel.')
            config['logchannel'] = str(id)
            await self.bot.db.config.update({'_id': str(ctx.guild.id)}, {'$set': config})
            await ctx.send(f'Mod-logs have been successfully set in <#{id}>')

    # ------------Welcome and leave----------------

    async def on_member_join(self, m):
        config = await self.bot.db.config.find_one({'_id': str(m.guild.id)})
        if not config:
            return
        try:
            type = config['welctype']
        except KeyError:
            return
        if type is False:
            return

        channel = int(config['welcchannel'])
        msg = config['welc']
        success = False
        i = 0
        while not success:
            try:
                await self.bot.get_channel(channel).send(msg.format(name=m, server=m.guild, mention=m.mention, member=m, membercount=len(m.guild.members)))
            except (discord.Forbidden, AttributeError):
                i += 1
            except IndexError:
                # the channel set doesn't allow remixbot to send messages
                pass
            else:
                success = True

    async def on_member_remove(self, m):
        config = await self.bot.db.config.find_one({'_id': str(m.guild.id)})
        if not config:
            return
        try:
            type = config['welctype']
        except KeyError:
            return
        if type is False:
            return

        channel = int(config['leavechannel'])
        msg = config['leave']
        success = False
        i = 0
        while not success:
            try:
                await self.bot.get_channel(channel).send(msg.format(name=m.name, server=m.guild, membercount=len(m.guild.members)))
            except (discord.Forbidden, AttributeError):
                i += 1
            except IndexError:
                # the channel set doesn't allow remixbot to send messages
                pass
            else:
                success = True

    # ------------Mod-log events below-------------

    async def logtype(self, item):
        config = await self.bot.db.config.find_one({'_id': str(item.guild.id)})
        if not config:
            return
        try:
            enabled = config['logtype']
        except KeyError:
            return
        else:
            if enabled:
                return True
            return False

    async def logchannel(self, item):
        config = await self.bot.db.config.find_one({'_id': str(item.guild.id)})
        if not config:
            return
        try:
            enabled = config['logtype']
            channel = self.bot.get_channel(int(config['logchannel']))
        except KeyError:
            return
        else:
            if enabled:
                return channel

    # async def on_message_delete(self, msg):
    #     if not self.logtype(msg)[0]:
    #         return
    #     em = discord.Embed(description=f'**Message sent by {msg.author.mention} deleted in {msg.channel.mention}**\n{msg.content}', color=discord.Color.red())
    #     em.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
    #     em.set_footer(f'ID: {msg.id}')
    #     await self.logtype(msg)[1].send(embed=em)

    async def on_guild_channel_create(self, channel):
        type = await self.logtype(channel)
        if not type:
            return
        em = discord.Embed(title='Channel Created', description=f'Channel {channel.mention} was created.', color=discord.Color.green())
        em.timestamp = datetime.datetime.utcnow()
        em.set_footer(text=f'ID: {channel.id}')
        ch = await self.logchannel(channel)
        await ch.send(embed=em)

    async def on_guild_channel_delete(self, channel):
        type = await self.logtype(channel)
        if not type:
            return
        em = discord.Embed(title='Channel Deleted', description=f'Channel {channel.mention} was deleted.', color=discord.Color.red())
        em.timestamp = datetime.datetime.utcnow()
        em.set_footer(text=f'ID: {channel.id}')
        ch = await self.logchannel(channel)
        await ch.send(embed=em)

    async def on_member_ban(self, guild, user):
        type = await self.logtype(user)
        if not type:
            return
        em = discord.Embed(description=f'`{user.name}` was banned from {guild.name}.', color=discord.Color.red())
        em.set_author(name=user.name, icon_url=user.avatar_url)
        em.set_footer(text=f'User ID: {user.id}')
        channel = await self.logchannel(user)
        await channel.send(embed=em)

    async def on_member_unban(self, guild, user):
        config = await self.bot.db.config.find_one({'_id': str(guild.id)})
        if not config:
            return
        try:
            enabled = config['logtype']
            channel = config['logchannel']
        except KeyError:
            return
        else:
            if enabled:
                channel = self.bot.get_channel(int(channel))
            else:
                return False
        em = discord.Embed(description=f'`{user.name}` was unbanned from {guild.name}.', color=discord.Color.green())
        em.set_author(name=user.name, icon_url=user.avatar_url)
        em.set_footer(text=f'User ID: {user.id}')
        await channel.send(embed=em)

    async def on_guild_role_create(self, role):
        type = await self.logtype(role)
        if not type:
            return
        em = discord.Embed(title='Role created', color=discord.Color.green(), description=f'Role `{role.name}` was created.')
        em.set_footer(text=f'Role ID: {role.id}')
        channel = await self.logchannel(role)
        await channel.send(embed=em)

    async def on_guild_role_delete(self, role):
        type = await self.logtype(role)
        if not type:
            return
        em = discord.Embed(title='Role deleted', color=discord.Color.red(), description=f'Role `{role.name}` was deleted.')
        em.set_footer(text=f'Role ID: {role.id}')
        channel = await self.logchannel(role)
        await channel.send(embed=em)


def setup(bot):
    bot.add_cog(Config(bot))
