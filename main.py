# main.py
import discord
from discord.ext import commands
import asyncio
from config import TOKEN, intents

# 봇 생성
bot = commands.Bot(command_prefix='!', intents=intents)

# Cog 파일들 목록
COGS_TO_LOAD = [
    "cogs.general",
    "cogs.cat_commands",
    "cogs.chatbot"
]

# Cog 로드 함수
async def load_extensions():
    for cog_name in COGS_TO_LOAD:
        try:
            await bot.load_extension(cog_name)
            print(f"성공적으로 '{cog_name}' Cog를 로드했습니다.")
        except commands.ExtensionNotFound:
            print(f"오류: '{cog_name}' Cog를 찾을 수 없습니다. 파일 경로를 확인하세요: `cogs/{cog_name.split('.')[-1]}.py`")
        except commands.ExtensionAlreadyLoaded:
            # 이미 로드된 경우 특별히 처리할 필요 없음
            print(f"정보: '{cog_name}' Cog는 이미 로드되어 있습니다.")
            pass
        except commands.NoEntryPointError:
            print(f"오류: '{cog_name}' Cog에 'async def setup(bot)' 함수가 정의되지 않았습니다.")
        except commands.ExtensionFailed as e:
            print(f"오류: '{cog_name}' Cog 로드 중 초기화 실패: {e.original}")
        except Exception as e:
            print(f"'{cog_name}' Cog 로드 중 알 수 없는 오류 발생: {e}")

@bot.event
async def on_ready():
    print(f'------------------------------------------------')
    print(f'{bot.user} (으)로 성공적으로 로그인했습니다!')
    print(f'봇 ID: {bot.user.id}')
    print(f'discord.py 버전: {discord.__version__}')
    print(f'------------------------------------------------')
    try:
        # 봇 상태 메시지 설정 (선택 사항)
        await bot.change_presence(activity=discord.Game(name="AI와 대화 | @멘션"))
    except Exception as e:
        print(f"상태 메시지 설정 중 오류: {e}")


# 봇 실행 메인 함수
async def main():
    if not TOKEN:
        print("치명적 오류: Discord 토큰이 제공되지 않았습니다. 프로그램을 종료합니다.")
        return

    # bot.start() 전에 Cog들을 로드하는 것이 일반적입니다.
    # discord.py 2.0+ 에서는 bot.setup_hook을 사용할 수도 있습니다.
    async with bot: # `async with bot:`을 사용하면 봇 종료 시 리소스 정리 용이
        await load_extensions()
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            print("치명적 오류: Discord 로그인 실패. 토큰이 유효한지 확인하세요.")
        except Exception as e:
            print(f"봇 실행 중 예기치 않은 오류 발생: {e}")

# 비동기 실행
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("사용자에 의해 봇이 종료되었습니다.")
    except Exception as e:
        # main() 함수 외부에서 발생할 수 있는 asyncio 관련 오류 등
        print(f"봇 실행 전/중 심각한 오류 발생: {e}")