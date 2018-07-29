import discord
from modules.botModule import *
import shlex
import time

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
        self.preprocessed_data = []
        self.refresh()

    def preprocess(self, field):
        # By default this method will take the designated field and make a title, omitting 'description'.
        # You may want to override this default behaviour to suit your table's needs.
        # The resulting embeds will be created with the order than the list is returned in.
        # Should return a 2-dimensional list of [title, data].
        self.processed_data = [[x[field], ''] for x in self.table]

    def refresh(self, *, field):
        self.processed_data.clear
        self.embeds.clear
        self.preprocess(self, field=field)
        counter = 1
        for item in self.processed_data:
            if counter == 1:
                # Just started the loop -- make a new embed object
                embed = discord.Embed(title=self.title, color=self.color)
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
            elif counter % self.limit == 0:
                # Last one in this embed object, now append and make a new object
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
                self.embeds.append(embed)
                del embed
                embed = discord.Embed(title=self.title, color=self.color)
            elif counter == len(self.preprocessed_data):
                # Last one in loop
                embed.add_field(name=item[0], value=item[1], inline=self.inline)
                self.embeds.append(embed)
                del embed
            else:
                # Else, nothing special needs to be done.
                embed = discord.Embed(title=self.title, color=self.color)
            counter += 1

    def next(self, *, current_pos):
        return self.embeds[(current_pos + 1) % self.limit]

    def previous(self, *, current_pos):
        return self.embeds[(current_pos - 1) % self.limit]

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
            if message.id == x.id:
                return True
        return False

    async def parse_command(self, message, client):
        embed = discord.Embed(title="Reaction based scrolling demo", color=0x000000)
        embed.add_field(name="One", value="Hello there!", inline=True)
        message_return = await client.send_message(message.channel, embed=embed)
        self.message_returns.append(message_return)
        await client.add_reaction(message_return, "⏪")
        await client.add_reaction(message_return, "⏩") # Ugh
        # TODO: change the addition of reactions into a loop

    # Now we hand off to the reaction command

    async def on_reaction_add(self, reaction, client, user):
        if not await self.contains_returns(reaction.message):
            return 0
        react_text = reaction.emoji
        if type(reaction.emoji) is not str:
            react_text = reaction.emoji.name
        if react_text == "⏪" or react_text == "⏩":
        # TODO: differentiate between different react_texts
            embed = discord.Embed(title="Reaction based scrolling demo", color=0x000000)
            embed.add_field(name="Two", value="General Kenobi!", inline=True)
            # TODO: be able to dynamically change what is edited
            await client.edit_message(reaction.message, embed=embed)
