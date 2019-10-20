"""Embeds capable of scrolling using discord reactions."""
from typing import List, Mapping, Any

import uuid

import discord
from discord.ext import commands


class ScrollView(commands.Cog):
    """Self-contained ScrollView."""
    def __init__(self, bot, message, embeds, id_: uuid.UUID):
        """Construct a single self-contained embed and the reaction handlers.

        Args:
            bot: commands.Bot instance to which this scrollable will belong.
            message: the discord message to which this embed is attached.
            embeds: the embeds representing the different pages of this scrollable.
            index: the current page (default 0).
            id_: the unique identifier of this ScrollView.
        """
        self.bot = bot
        self.message = message
        self.embeds = embeds
        self.name = str(id_)
        self.index = 0

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, _):
        """Reaction listener for ScrollView.

        When a reaction is detected on the message associated with this ScrollView,
        the page is advanced or reversed accordingly.
        """
        if reaction.message != self.message:
            return

        react_text = reaction.emoji
        if not isinstance(reaction.emoji, str):
            react_text = reaction.emoji.name
        if react_text == "⏩":
            await reaction.message.edit(embed=self.next())
        if react_text == "⏪":
            await reaction.message.edit(embed=self.previous())

    def next(self) -> discord.Embed:
        """Update the current scrollable to the next page and return the embed.

        Loops if the current page is the last one prior to change.
        """
        self.index = (self.index + 1) % len(self.embeds)
        return self.embeds[self.index]

    def previous(self) -> discord.Embed:
        """Update the current scrollable to the previous page and return the embed.

        Loops if the current page is the first one prior to change.
        """
        self.index = (self.index - 1) % len(self.embeds)
        return self.embeds[self.index]

    def current(self):
        """Return the embed for the current page."""
        return self.embeds[self.index]


class ScrollViewBuilder:
    """Builder object for ScrollViews."""
    def __init__(self, color: int, title: str, inline: bool, bot: commands.Bot):
        """Creates a builder for ScrollViews.

        Args:
            color: The color used by the ScrollViews produced by this builder.
            title: The default color used by this builder.
            inline: Boolean indicating whether to inline the embed.
            bot: the commands.Bot which owns the ScrollViews.
        """
        self.color = color
        self.title = title
        self.inline = inline
        self.bot = bot
        self.views = []

    async def create_with(self, ctx: commands.Context, data: List[Mapping[Any, Any]],
                          **kwargs) -> ScrollView:
        """Creates a ScrollView for the given data."""
        embeds = ScrollViewBuilder._create_embeds(data, **kwargs)
        message = ctx.send(embed=embeds[0])
        await message.add_reaction("⏪")
        await message.add_reaction("⏩")

        self.views.append(uuid.uuid4())
        view = ScrollView(self.bot, embeds, message, id_=self.views[-1])
        self.bot.add_cog(view)

        return view

    async def create_on_message(self, message, data: List[Mapping[Any, Any]],
                                **kwargs) -> ScrollView:
        """Creates a ScrollView associated with a message that already exists."""
        embeds = ScrollViewBuilder._create_embeds(data, **kwargs)
        message.edit(embed=embeds[0])
        await message.add_reaction("⏪")
        await message.add_reaction("⏩")

        self.views.append(uuid.uuid4())
        view = ScrollView(self.bot, embeds, message, id_=self.views[-1])
        self.bot.add_cog(view)

        return view

    def clear(self):
        """Stop monitoring all current ScrollViews."""
        for cog in self.views:
            self.bot.remove_cog(str(cog))
        self.views = []

    def _create_embeds(self,
                       data: List[Mapping[Any, Any]],
                       **kwargs) -> List[discord.Embed]:
        title = kwargs.get('title', self.title)
        key_str = kwargs.get('key_str', None)
        value_str = kwargs.get('value_str', None)

        embeds = list()
        for page in data:
            embed = discord.Embed(
                title=title,
                color=self.color)

            for key, value in page.items():
                key = key_str(key) if key_str else str(key)
                value = value_str(value) if value_str else str(value)
                embed.add_field(name=key, value=value)
            embeds.append(embed)
        return embeds
