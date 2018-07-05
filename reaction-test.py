import discord
from modules.botModule import *
import shlex
import time

class ReactionTest(BotModule):
    name = 'reactiontest'

    description = 'Testing reaction based scrolling'

    help_text = '`!reactiontest` to trigger a demo.'

    trigger_string = 'reactiontest'

    module_version = '1.0.0'

    listen_for_reactions = True


    # Instead of using TinyDB, since scubot can't work with reactions persistently a list should be used
    message_returns = []

    async def parse_command(self, message, client):
        embed = discord.Embed(title="Reaction based scrolling demo", color=0x000000)
        embed.add_field(name="One", value="Hello there!", inline=True)
        message_return = await client.send_message(message.channel, embed=embed)
        self.message_returns.append(message_return)
        client.add_reaction(message_return, ":rewind:")
        client.add_reaction(message_return, ":fast_forward:")

    # Now we hand off to the reaction command

    async def on_reaction_add(self, reaction, client, user):
        if reaction.message.id not in self.message_returns:
            return 0

        react_text = reaction.emoji
        if type(reaction.emoji) is not str:
            react_text = reaction.emoji.name
        if react_text == ":rewind:" or react_text == ":fast_forward:":
            embed = discord.Embed(title="Reaction based scrolling demo", color=0x000000)
            embed.add_field(name="Two", value="General Kenobi!", inline=True)
            client.edit_message(reaction.message, embed=embed)
