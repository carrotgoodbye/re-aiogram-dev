from re_aiogram import Bot, Message
from re_aiogram.filters import Command, F

bot = Bot(env_token="API_TOKEN")


@bot.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello from re_aiogram!")


@bot.message(F.text, ~F.text.startswith("/"))
async def echo(message: Message):
    await message.answer(f"You said: {message.text}")


bot.run()
