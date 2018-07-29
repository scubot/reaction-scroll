import discord
from modules.botModule import *
from tinydb import TinyDB, Query
import shlex
import time
import math

class Scrollable():
    # This object provides an easy way to turn a TinyDB table into a scrollable embed.
    # However, scrolling logic is not included in this object.
    def __init__(self, *, limit, color, table, title, inline):
        self.color = color
        self.limit = limit
        self.table = table
        self.title = title
        self.inline = inline
        self.embeds = []
        self.processed_data = []

    def preprocess(self, field):
        # By default this method will take the designated field and make a title, omitting 'description'.
        # You may want to override this default behaviour to suit your table's needs.
        # The resulting embeds will be created with the order than the list is returned in.
        # Should return a 2-dimensional list of [title, data].
        self.processed_data = [[x[field], 'Testing'] for x in self.table]

    def refresh(self, *, field):
        self.processed_data.clear()
        self.embeds.clear()
        self.preprocess(field=field)
        counter = 1
        page = 1
        for item in self.processed_data:
            page = math.ceil(counter/self.limit)
            if counter == 1:
                # Just started the loop -- make a new embed object
                embed = discord.Embed(title=self.title, color=self.color)
                embed.set_footer(text="Page " + str(page) + " of " + str(math.ceil(len(self.processed_data)/self.limit)))
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
            elif counter % self.limit == 0:
                # Last one in this embed object, now append and make a new object
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
                self.embeds.append(embed)
                del embed
                embed = discord.Embed(title=self.title, color=self.color)
                embed.set_footer(text="Page " + str(page+1) + " of " + str(math.ceil(len(self.processed_data)/self.limit)))
            elif counter == len(self.processed_data):
                # Last one in loop
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
                self.embeds.append(embed)
                del embed
            else:
                # Else, nothing special needs to be done.
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
            counter += 1

    def next(self, *, current_pos):
        return self.embeds[(int(current_pos) + 1) % len(self.embeds)]

    def previous(self, *, current_pos):
        return self.embeds[(int(current_pos) - 1) % len(self.embeds)]

    def initial_embed(self):
        return self.embeds[0]

class ReactionTest(BotModule):
    name = 'reactiontest'

    description = 'Testing reaction based scrolling'

    help_text = '`!reactiontest` to trigger a demo.'

    trigger_string = 'reactiontest'

    module_version = '1.0.0'

    listen_for_reaction = True

    # Instead of using TinyDB, since scubot can't work with reactions persistently a list should be used
    message_returns = []

    async def contains_returns(self, message):
        for x in self.message_returns:
            if message.id == x[0].id:
                return True
        return False

    async def find_pos(self, message):
        for x in self.message_returns:
            if message.id == x[0].id:
                return x[1]

    async def update_pos(self, message, ty):
        for x in self.message_returns:
            if message.id == x[0].id:
                if ty == 'next':
                    x[1] += 1
                if ty == 'prev':
                    x[1] -= 1

    async def parse_command(self, message, client):
        self.module_db.purge()
        for x in range(1, 16):
            self.module_db.insert({'foo': x})
        self.scroll = Scrollable(limit=4, color=0xc0fefe, table=self.module_db, title="Demo", inline=True)
        self.scroll.refresh(field='foo')
        message_return = await client.send_message(message.channel, embed=self.scroll.initial_embed())
        self.message_returns.append([message_return, 0])
        await client.add_reaction(message_return, "⏪")
        await client.add_reaction(message_return, "⏩") # Ugh

    # Now we hand off to the reaction command

    async def on_reaction_add(self, reaction, client, user):
        if not await self.contains_returns(reaction.message):
            return 0
        pos = await self.find_pos(reaction.message)
        react_text = reaction.emoji
        if type(reaction.emoji) is not str:
            react_text = reaction.emoji.name
        if react_text == "⏩":
            embed = self.scroll.next(current_pos=pos)
            await client.edit_message(reaction.message, embed=embed)
            await self.update_pos(reaction.message, 'next')
        if react_text == "⏪":
            embed = self.scroll.previous(current_pos=pos)
            await client.edit_message(reaction.message, embed=embed)
            await self.update_pos(reaction.message, 'prev')
