import discord
from discord.ext import commands
import random

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} (으)로 로그인 성공!')
        print(f'봇 ID: {self.bot.user.id}')
        print('------')
        print('봇이 준비되었습니다!')

    @commands.command(name='안녕')
    async def hello(self, ctx):
        await ctx.send('안녕하세요! 만나서 반가워요!')

    @commands.command(name='따라해')
    async def echo(self, ctx, *, message: str):
        await ctx.send(message)

    @commands.command(name='8ball', aliases=['8볼'])
    async def eight_ball(self, ctx):
        await ctx.send(random.choice([
            "네, 확실합니다.",
            "아마도 그렇습니다.",
            "확실하지 않습니다.",
            "아니요, 절대 아닙니다.",
            "다시 물어보세요.",
            "지금은 대답할 수 없습니다."
        ]))

    @commands.command(name='도움')
    async def help_command(self, ctx):
        help_message = (
            "!도움 - 이 도움말을 보여줍니다.\n"
            "!안녕 - 인사합니다.\n"
            "!따라해 [할말] - 봇이 [할말]을 따라합니다.\n"
            "!8ball/8볼 [질문] - 질문에 대답합니다.\n"
            "!콩아/울어 - 콩이를 부릅니다.\n"
            "!손/발 - :feet:\n"
            "!돌아 - 콩이가 돕니다.\n"
            "!빵/빵야 - :gun: BANG.\n"
            "!앉아 - 콩이가 앉습니다.\n"
            "!오예 - :dancer: :musical_note: :man_dancing:\n"
            "!nyan/냥 - :rainbow_flag:\n"
        )
        await ctx.send(help_message)

async def setup(bot):
    await bot.add_cog(General(bot))