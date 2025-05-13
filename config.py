# config.py
import discord
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Discord 토큰
TOKEN = os.getenv('DISCORD_TOKEN')

# Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Gemini 모델 설정
GEMINI_MODEL_NAME = 'gemini-2.0-flash'

# Intents
intents = discord.Intents.default()
intents.message_content = True 