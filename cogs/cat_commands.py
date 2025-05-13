import discord
from discord.ext import commands

class CatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='콩아', aliases=["울어"])
    async def meow(self, ctx):
        await ctx.reply('야옹')

    @commands.command(name='손', aliases=['발'])
    async def paw(self, ctx):
        await ctx.send("""```       .::::::::::.:::.       
      -.              .:      
     -   :===:   -==-.  -     
   :-:  .====-  :====:  :-:   
 :.      :===:  .-==-.     .: 
:.  :=-:              .-=:. .:
-  :====:   :-==-:   .====-  -
:. :===-.  -======-  .-===: .:
.:   .   -==========-.  .   : 
 :      :============:     .: 
 :.     .-==========-.     .. 
 .:       .::-==--:.       :. 
  :                       .:  
  ..                      ..  
  ..                      ..  
  ..                      ..  
  :.                      .:  
  :.                      .:  
  :                        :  
  :                        :  
 .:                        :. 
 .:                        :. ```""")

    @commands.command(name='돌아')
    async def oiia(self, ctx):
        await ctx.send("https://media.tenor.com/sbfBfp3FeY8AAAAi/oia-uia.gif")
        await ctx.send("oiiai oiiai oiiai oii")

    @commands.command(name='빵', aliases=['빵야'])
    async def bang(self, ctx):
        await ctx.send(":gun:")
        await ctx.send("https://c.tenor.com/GHDZ0NxSPp4AAAAd/tenor.gif")
        
    @commands.command(name='앉아')
    async def sit(self, ctx):
        await ctx.send("https://media.tenor.com/DsQEmWY2Ry0AAAAi/cat-sitting.gif")

    @commands.command(name='오예')
    async def dance(self, ctx):
        await ctx.send("https://c.tenor.com/1kf4J-xC_68AAAAC/tenor.gif")

    @commands.command(name='nyan', aliases=['냥'])
    async def nyan(self, ctx):
        await ctx.send("https://c.tenor.com/2roX3uxz_68AAAAC/tenor.gif")

async def setup(bot):
    await bot.add_cog(CatCommands(bot))