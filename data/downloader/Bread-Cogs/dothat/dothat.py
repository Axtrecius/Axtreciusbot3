import discord
from discord.ext import commands


class DoThat:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dothat", aliases=['dt'], pass_context=True)
    async def _dothat(self, ctx, user: discord.Member=None, *, do_this):
        """Do anything, to anyone, anytime.

        Example: ?dothat @BakersBakeBread laugh's at
            >> YourUserName laugh's at BakersBakeBread"""
        author = ctx.message.author

        payload =\
        ("`{}` _**{}**_ `{}`".format(author.name, do_this, user.name))
        if user == author:
            await self.bot.say("You can't do that to yourself!")
        else:
            await self.bot.say(payload)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass


def setup(bot):
    bot.add_cog(DoThat(bot))
