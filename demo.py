import discord
from modules.botModule import *
from tinydb import TinyDB, Query
import shlex
import time
import math
import reactionscroll

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
        self.scroll = reactionscroll.Scrollable(limit=4, color=0xc0fefe, table=self.module_db, title="Demo", inline=True)
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
