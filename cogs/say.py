import discord
from discord.ext import commands
from .utils import checks

class Say:
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(administrator=True)
    async def say(self, ctx): 
        """Make your bot say something in the channel you use the command in."""

        msg = ctx.message.content
        message = ctx.message
        author = ctx.message.author
        
        msg = msg[5:]
        try:
            await self.bot.delete_message(message)
            
        except discord.Forbidden:
            print("No permissions.")

            def error(self, ctx):
                embed=discord.Embed(
                    title="Error:",
                    description="Unable to delete the command message, I don't have the adminstrative permissions to do so.",
                    color=0x207cee)
                return embed           

            Msg = error(self, ctx)
            await self.bot.whisper(author, embed=Msg)
        try:
            await self.bot.say(msg)
        except discord.errors.HTTPException:
            def error2(self, ctx):
                embed=discord.Embed(
                    title="Error:",
                    description="Unable to send text. Its empty. :upside_down: ",
                    color=0x207cee)
                return embed
            Msg2 = error2(self, ctx)
            await self.bot.whisper(author, embed=Msg2)
            
def setup(bot):
    bot.add_cog(Say(bot))
