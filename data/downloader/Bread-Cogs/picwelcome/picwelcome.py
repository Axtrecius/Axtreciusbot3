try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    pil_available = True
except:
    pil_available = False
import discord
import asyncio
from cogs.utils import checks
import aiohttp
import os
from .utils.dataIO import dataIO
from discord.ext import commands
from discord.utils import find
from __main__ import send_cmd_help

class PicWelcome:
    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/picwelcome/settings.json")


        if "userbar" not in self.settings.keys():
            self.settings["userbar"] = {}
            for server in self.bot.servers:
                self.settings["userbar"][server.id] = {
                    "background" : "data/picwelcome/bg.png"
                }
            self.settings.pop("background", None)
            dataIO.save_json("data/picwelcome/settings.json", self.settings)


    @checks.admin_or_permissions(manager_server=True)
    @commands.group(pass_context=True)
    async def picwelcome(self, ctx):
        """Welcome users to your server with an image."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)


    @checks.admin_or_permissions(manager_server=True)
    @picwelcome.group(pass_context=True)
    async def channel(self, ctx, channel:discord.Channel=None):
        """Set the channel you want members to welcomed in"""

        if channel is None:
            channel = ctx.message.channel
        self.settings["userbar"][ctx.message.server.id]["channel"] = channel.id
        self.set_server = self.bot.get_channel(self.settings["userbar"][ctx.message.server.id]["channel"])
        dataIO.save_json("data/picwelcome/settings.json", self.settings)
        channel = self.set_server
        try:
            await self.bot.send_message(channel, "I will welcome new users here.")
        except discord.errors.Forbidden:
            await self.bot.send_message(channel, 
                "I need the \"Send Files\" permission to send messages here.")

    @picwelcome.command(pass_context = True)
    @checks.serverowner_or_permissions(manage_server=True)
    async def background(self, ctx, default = None):
        """Sets the background for welcome message"""

        # check if we want to reset
        if default is not None:
            self.settings["userbar"][ctx.message.server.id]["background"] = "data/picwelcome/bg.png"
            dataIO.save_json("data/picwelcome/settings.json", self.settings)
            await self.bot.say("I will now use default image as a background")

        else:

            # request image from user
            await self.bot.say(
                "Please send the background. It should be 400x100"
                " and one of these formats: `.png`, `.tiff`, `.bmp`, `.gif`"
                )
            answer = await self.bot.wait_for_message(author=ctx.message.author,
                                                     channel=ctx.message.channel,
                                                     check=lambda m: any(m.attachments),
                                                     timeout=15)
            bg_image = Image

            if answer.attachments[0]['filename']:
                await self.bot.say("Image success :{}".format(answer.attachments[0]['filename']))

                # download the image
                gateway = answer.attachments[0]['url']
                payload = {}
                payload['limit'] = 1
                headers = {'user-agent': 'Python-Red-cog/2.0'}
                try:
                    session = aiohttp.ClientSession()
                    if not os.path.exists("data/picwelcome/" + ctx.message.server.id):
                        os.makedirs("data/picwelcome/" + ctx.message.server.id)
                    async with session.get(gateway, params=payload, headers=headers) as r:
                        image = await r.read()
                        with open("data/picwelcome/" + ctx.message.server.id + '/custom_bg', "wb") as f:
                            f.write(image)
                            await self.bot.say(answer.attachments[0]['filename'] + ' downloaded')
                    session.close()
                except Exception as x:
                    await self.bot.say('Sentry fucked up\n\n{}'.format(x))
                    
                try:
                    with open('data/picwelcome/' + ctx.message.server.id + '/custom_bg','wb') as f:
                        f.write(image)
                        bg_image = Image.open('data/picwelcome/' + ctx.message.server.id + '/custom_bg').convert('RGB')
                        success = True

                except Exception as e:
                    success = False
                    print(e)

                if success:

                    # check dimensions
                    if bg_image.size == (400,100):
                        self.settings["userbar"][ctx.message.server.id]["background"] = "data/picwelcome/" + ctx.message.server.id + "/custom_bg"
                        dataIO.save_json("data/picwelcome/settings.json", self.settings)
                        await self.bot.say("Using image as welcome background.")
                    else:
                        await self.bot.say("Image has the wrong dimensions, please provide 400x100 image")
                else:
                    await self.bot.say("That image isn't valid.")
            else:
                await self.bot.say("Couldn't get the image")

    # @commands.command(pass_context = True)
    async def text(self, member):
        """Welcome users with an image!"""
        server = member.server
        channel = self.bot.get_channel(self.settings["userbar"][server.id]["channel"])
        avatar_url = member.avatar_url
        avatar_image = Image

        try: #get user avatar
            async with aiohttp.get(avatar_url) as r:
                image = await r.content.read()
            with open('data/picwelcome/temp_avatar','wb') as f:
                f.write(image)
                success = True
        except Exception as e:
            success = False
            print(e)


        avatar_image = Image.open('data/picwelcome/temp_avatar').convert('RGBA')

        result = Image.open(self.settings["userbar"][server.id]["background"]).convert('RGBA')

        process = Image.new('RGBA', (400,100), (0,0,0))

        # get a font
        fnt = ImageFont.truetype('data/drawing/font.ttf', 37)
        fnt_sm = ImageFont.truetype('data/drawing/font.ttf', 20)

        # get a drawing context
        drawthis = ImageDraw.Draw(process)

        sign = member.name
        if len(sign) > 20:
            sign = member.name[:20] + ".."

        # calculate text position
        author_width = fnt_sm.getsize(sign)[0]

        drawthis.rectangle([(0,0),(400,100)], fill=(0,0,0,160))
        drawthis.text((25,25), sign, font=fnt, fill=(255,255,255,255))
        drawthis.text((25,65), "Welcome to " + member.server.name, font=fnt_sm, fill=(255,255,255,255))
        drawthis.rectangle([(10,10),(390,90)], fill=None, outline=(200,200,200,128))
        
        avatar_image = avatar_image.resize(size=(60,60))
        
        process.paste(avatar_image, (320, 20))

        result = Image.alpha_composite(result, process)

        result.save('data/picwelcome/temp.png','PNG', quality=100)
        await self.bot.send_file(channel, 'data/picwelcome/temp.png')

        os.remove('data/picwelcome/temp.png')

def check_folder():
    if not os.path.exists('data/picwelcome'):
        os.makedirs('data/picwelcome')

def check_files():
    if not os.path.exists("data/picwelcome/settings.json"):
        print("Creating empty ignores.json...")
        data = {}

        dataIO.save_json("data/picwelcome/settings.json", data)
def setup(bot):
    if pil_available is False:
        raise RuntimeError("You don't have Pillow installed, run\n```pip3 install pillow```And try again")
        return
    check_folder()
    check_files()  #who created these?
    n = PicWelcome(bot)
    bot.add_listener(n.text,"on_member_join")
    bot.add_cog(n)