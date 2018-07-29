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
