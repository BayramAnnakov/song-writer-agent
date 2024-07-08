import dotenv

dotenv.load_dotenv()

import os

from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

from suno import custom_generate_audio

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

def create_song(lyrics:str, style:str, title:str):
    """Create a song with the given lyrics, style and title."""
    response = custom_generate_audio(lyrics, style, title)

    audio_urls = [item['audio_url'] for item in response]

    return audio_urls[0]


create_song_tool = FunctionTool.from_defaults(fn=create_song)

llm = OpenAI(model="gpt-4o")
agent = OpenAIAgent.from_tools([create_song_tool], llm=llm, verbose=True, system_prompt="""
You are AI song generator. Given a text prompt, you will generate lyrics in a given style, and then generate a song based on those lyrics.""")

def generate_song_command(topic:str, style:str="rap"):
    """Generate a song based on the given topic."""
    agent.chat(f"Create lyrics in the style of {style} song about the following topic: {topic}")

    agent.chat("Create a song based on the generated lyrics")

    response = agent.chat("Print the audio url of the generated song")

    return str(response)

TOPIC, STYLE = range(2)

async def start(update, context):
    await update.message.reply_text("What is the topic of the song?")
    return TOPIC

async def topic(update, context):
    context.user_data['topic'] = update.message.text

    await update.message.reply_text("What is the style of the song?")
    return STYLE

async def style(update, context):
    context.user_data['style'] = update.message.text

    response = generate_song_command(context.user_data['topic'], context.user_data['style'])

    await update.message.reply_text(response)

    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Bye!")
    return ConversationHandler.END

def main():
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TOPIC: [MessageHandler(filters.TEXT, topic)],
            STYLE: [MessageHandler(filters.TEXT, style)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conversation_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()