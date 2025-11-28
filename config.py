import os

from dotenv import load_dotenv


load_dotenv()


TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "score_data.json"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

P1_NAME = "Никита"
P1_KEY = "nikita"
P2_NAME = "Даша"
P2_KEY = "dasha"

EMOJI_P1 = "🐻"
EMOJI_P2 = "🐱"
EMOJI_HEART = "⭐"
EMOJI_WISH = "✨"
