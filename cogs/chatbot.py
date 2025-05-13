# cogs/chatbot.py
import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME
import os
from dotenv import load_dotenv

# 기본 페르소나 
DEFAULT_PERSONALITY = os.getenv('DEFAULT_BOT_PERSONALITY')

# 다른 페르소나 딕셔너리
# AVAILABLE_PERSONALITIES = {}

class ChatBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model_name = GEMINI_MODEL_NAME
        # 각 채널별 대화 세션 및 현재 적용된 페르소나를 저장
        # { channel_id: {'session': ChatSession, 'persona_prompt': str} }
        self.channel_conversations = {}
        self.gemini_ready = False
        
        # 현재 전역적으로 적용될 페르소나 프롬프트
        self.current_global_persona_prompt = DEFAULT_PERSONALITY

        if not GEMINI_API_KEY:
            print("ChatBot Cog: Gemini API 키가 설정되지 않았습니다. 대화 기능을 사용할 수 없습니다.")
            return

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # start_chat의 history를 통해 페르소나 전달
            self.model = genai.GenerativeModel(self.model_name)
            print(f"ChatBot Cog: Gemini 모델 ({self.model_name})이 성공적으로 초기화되었습니다.")
            self.gemini_ready = True
        except Exception as e:
            print(f"ChatBot Cog: Gemini API 초기화 중 오류 발생: {e}")

    def _create_initial_history_with_persona(self, persona_prompt: str):
        """페르소나 설정을 포함한 초기 대화 기록 리스트를 생성합니다."""
        if not persona_prompt:
            return [] 

        # 모델에게 페르소나를 명확히 지시하고, 모델이 이를 인지했다는 응답을 유도
        return [
            {
                'role': 'user',
                'parts': [
                    f"시스템 지시: 지금부터 너는 다음 페르소나 설명을 따라야 한다. 이 페르소나를 완벽하게 숙지하고 사용자의 다음 메시지부터 적용하여 응답하라.\n\n"
                    f"--- 페르소나 시작 ---\n{persona_prompt}\n--- 페르소나 끝 ---"
                ]
            },
            {
                'role': 'model',
                'parts': [
                    f"알겠습니다! 제시해주신 페르소나를 완벽히 이해했습니다. 이제부터 해당 페르소나에 맞춰 사용자님과 즐겁게 대화하겠습니다! 무엇을 도와드릴까요? 😊"
                ]
            }
        ]

    async def _get_or_create_chat_session(self, channel_id: int):
        """
        채널 ID에 대한 채팅 세션을 가져오거나, 페르소나를 적용하여 새로 생성합니다.
        페르소나가 변경된 경우 기존 세션을 삭제하고 새로 생성합니다.
        """
        current_persona_for_channel = self.current_global_persona_prompt # 현재 적용된 전역 페르소나 사용

        # 채널에 이미 세션이 있고, 페르소나가 변경되지 않았다면 기존 세션 반환
        if channel_id in self.channel_conversations:
            convo_data = self.channel_conversations[channel_id]
            if convo_data.get('persona_prompt') == current_persona_for_channel and convo_data.get('session'):
                return convo_data['session']
            else: # 페르소나가 변경되었거나 세션이 없는 경우 (이론상 발생하면 안됨)
                del self.channel_conversations[channel_id] # 기존 데이터 삭제

        # 새 세션 생성 또는 페르소나 변경으로 인한 재생성
        initial_history = self._create_initial_history_with_persona(current_persona_for_channel)
        new_session = self.model.start_chat(history=initial_history)
        self.channel_conversations[channel_id] = {
            'session': new_session,
            'persona_prompt': current_persona_for_channel
        }
        print(f"ChatBot Cog: 채널 {channel_id}에 새 대화 세션 생성 (페르소나 적용됨).")
        return new_session

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.gemini_ready or message.author == self.bot.user or message.author.bot:
            return

        if self.bot.user.mentioned_in(message):
            prompt_text = message.content
            for mention in message.mentions:
                if mention == self.bot.user:
                    prompt_text = prompt_text.replace(f'<@!{mention.id}>', '').replace(f'<@{mention.id}>', '')
            prompt_text = prompt_text.strip()

            if not prompt_text:
                # 페르소나에 맞는 기본 인사 (예시, 실제로는 모델이 생성하도록 유도)
                # 이 부분은 모델이 초기 history에 따라 응답하도록 둘 수 있습니다.
                # 또는, 간단한 고정 응답을 할 수도 있습니다.
                # 여기서는 모델에게 빈 프롬프트를 보내 페르소나 기반 인사를 유도합니다.
                # 다만, 모델이 빈 프롬프트에 어떻게 반응할지는 테스트 필요.
                # 더 안정적인 방법은 아래처럼 고정된 환영 메시지를 보내는 것입니다.
                # await message.reply(f"안녕하세요! 저는 {self.current_global_persona_prompt.splitlines()[0].split(' ')[-1].replace('이야.','')}예요! 무엇을 도와드릴까요? 😊") # 첫 줄에서 이름 추출 (가정)
                # 또는, 모델에게 "안녕"이라고 보내서 페르소나 인사를 유도
                # prompt_text = "안녕!" # 이렇게 하면 아래 로직으로 처리됨
                await message.reply(f"안녕하세요! 저를 부르셨네요. 무엇을 도와드릴까요? 😊")
                return

            channel_id = message.channel.id
            chat_session = await self._get_or_create_chat_session(channel_id)

            async with message.channel.typing():
                try:
                    response = await asyncio.to_thread(chat_session.send_message, prompt_text)
                    reply_text = response.text

                    if len(reply_text) > 1950:
                        chunks = [reply_text[i:i + 1950] for i in range(0, len(reply_text), 1950)]
                        for i, chunk in enumerate(chunks):
                            if i == 0: await message.reply(chunk)
                            else: await message.channel.send(chunk)
                    elif reply_text:
                        await message.reply(reply_text)
                    else:
                        await message.reply("죄송합니다, 적절한 답변을 생성할 수 없었습니다. (응답 내용 없음)")

                except ValueError as ve:
                    if "empty Candidate.content" in str(ve).lower() or "blocked" in str(ve).lower():
                        print(f"ChatBot Cog: Gemini API가 응답을 반환하지 않았습니다 (Safety Filter 등). 프롬프트: '{prompt_text}', 상세: {ve}")
                        await message.reply("죄송합니다, 요청하신 내용에 대한 답변을 생성할 수 없습니다. (콘텐츠 안전 문제 또는 API 응답 없음)")
                    else:
                        print(f"ChatBot Cog: Gemini API 처리 중 값 오류 발생: {type(ve).__name__} - {ve}")
                        await message.reply(f"죄송합니다, 응답을 생성하는 중 문제가 발생했습니다. (값 오류)")
                except Exception as e:
                    print(f"ChatBot Cog: Gemini API 호출 중 예상치 못한 오류 발생 (채널: {message.channel.id})")
                    print(f"오류 타입: {type(e).__name__}, 오류 메시지: {e}")
                    import traceback
                    traceback.print_exc()
                    await message.reply("죄송합니다, 응답을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

    @commands.command(name="페르소나설정", aliases=["set_persona"])
    @commands.has_permissions(administrator=True)
    async def set_persona(self, ctx: commands.Context, *, persona_description: str = None):
        """
        봇의 페르소나를 설정합니다.
        설명 없이 사용하면 기본 페르소나로 설정됩니다.
        변경 사항은 새 대화부터 적용되며, 기존 대화는 초기화해야 합니다.
        """
        if not self.gemini_ready:
            await ctx.reply("죄송합니다, 현재 대화 기능에 문제가 있어 페르소나를 설정할 수 없습니다.")
            return

        if persona_description and persona_description.strip():
            self.current_global_persona_prompt = persona_description.strip()
            action_message = f"봇의 페르소나가 다음과 같이 설정되었습니다:\n```\n{self.current_global_persona_prompt}\n```"
        else:
            self.current_global_persona_prompt = DEFAULT_PERSONALITY
            action_message = f"봇의 페르소나가 기본값으로 재설정되었습니다."
        
        # 모든 채널의 기존 대화 세션 데이터 삭제 (새 페르소나 즉시 반영 위해)
        # 이렇게 하면 다음 메시지부터 새 페르소나가 적용된 세션이 생성됩니다.
        cleared_channels = len(self.channel_conversations)
        self.channel_conversations.clear() 
        
        await ctx.reply(f"{action_message}\n모든 채널의 기존 대화가 초기화되어 새 페르소나가 다음 대화부터 적용됩니다. (초기화된 대화 수: {cleared_channels})")

    @commands.command(name="현재페르소나", aliases=["get_persona", "show_persona"])
    async def show_current_persona(self, ctx: commands.Context):
        """현재 설정된 봇의 페르소나 설명을 보여줍니다."""
        if not self.gemini_ready:
            await ctx.reply("죄송합니다, 현재 대화 기능에 문제가 있어 페르소나 정보를 가져올 수 없습니다.")
            return
        
        persona_to_show = self.current_global_persona_prompt if self.current_global_persona_prompt else "설정된 페르소나가 없습니다 (기본 동작)."
        embed = discord.Embed(title="🤖 현재 봇 페르소나", description=f"```\n{persona_to_show}\n```", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name="대화초기화", aliases=["reset_chat", "clear_chat"])
    @commands.cooldown(1, 10, commands.BucketType.channel) # 채널당 10초에 한 번
    async def reset_channel_conversation(self, ctx: commands.Context):
        """현재 채널의 Gemini 대화 기록을 초기화하고 새 페르소나를 적용합니다."""
        if not self.gemini_ready:
            await ctx.reply("죄송합니다, 현재 대화 기능에 문제가 있어 기록을 초기화할 수 없습니다.")
            return

        channel_id = ctx.channel.id
        if channel_id in self.channel_conversations:
            del self.channel_conversations[channel_id]
            await ctx.reply(f"{ctx.channel.mention} 채널의 대화 기록이 초기화되었습니다. 다음 대화부터 현재 설정된 페르소나가 적용됩니다.")
        else:
            await ctx.reply(f"{ctx.channel.mention} 채널에는 초기화할 대화 기록이 없습니다. (새 대화는 자동으로 현재 페르소나로 시작됩니다)")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"이 명령어는 현재 재사용 대기시간 중입니다. {error.retry_after:.2f}초 후에 다시 시도해주세요.", delete_after=5)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("이 명령어를 사용할 권한이 없습니다.", delete_after=10)
        elif isinstance(error, commands.CommandNotFound):
            pass # 존재하지 않는 명령어는 조용히 무시하거나, 사용자에게 알릴 수 있음
        else:
            print(f"명령어 처리 중 예외 발생: {type(error).__name__} - {error}")
            # 개발 중에는 상세 오류를 출력하는 것이 좋음
            # await ctx.send("명령어 실행 중 오류가 발생했습니다.", delete_after=10)


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatBot(bot))