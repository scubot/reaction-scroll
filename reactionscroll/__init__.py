from typing import List, Mapping, Any

import discord
from discord.ext import commands


class ScrollView(commands.Cog):
    def __init__(self, bot, message, embeds, index=0):
        self.bot = bot
        self.message = message
        self.embeds = embeds
        self.index = index

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message != self.message:
            return

        react_text = reaction.emoji
        if type(reaction.emoji) is not str:
            react_text = reaction.emoji.name
        if react_text == "⏩":
            await reaction.message.edit(embed=self.next())
        if react_text == "⏪":
            await reaction.message.edit(embed=self.previous())

    def next(self) -> discord.Embed:
        self.index = (self.index + 1) % len(self.embeds)
        return self.embeds[self.index]

    def previous(self, *, current_pos) -> discord.Embed:
        self.index = (self.index - 1) % len(self.embeds)
        return self.embeds[self.index]

    def current(self):
        return self.embeds[self.index]


class ScrollViewBuilder:
    def __init__(self, color, title, inline, bot: commands.Bot):
        self.color = color
        self.title = title
        self.inline = inline
        self.bot = bot

    def create_with(self, data: List[Mapping[Any, Any]], ctx: commands.Context,
                    key_str=None,
                    value_str=None) -> ScrollView:
        embeds = list()
        for page in data:
            embed = discord.Embed(
                title=self.title,
                color=self.color)

            for k, v in page.items():
                k = key_str(k) if key_str else str(k)
                v = value_str(v) if value_str else str(v)
                embed.add_field(name=k, value=v)
            embeds.append(embed)

        message = ctx.send(embed=embeds[0])

        view = ScrollView(self.bot, embeds, message)
        self.bot.add_cog(view)

        return view
