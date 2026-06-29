from src.re_aiogram import Bot, Message
from src.re_aiogram.filters import Command

bot = Bot(env_token="API_TOKEN")


@bot.message(Command("start"))
async def start(message: Message):
    await message.answer("What is your name?")
    message.next_step(ask_name)

async def ask_name(message: Message):
    name = message.text
    await message.answer(f"Hii, {name}! How old are you?")
    message.next_step(lambda m: ask_age(m, name))

async def ask_age(message: Message, name: str):
    try:
        age = int(message.text)
        await message.answer(f"{name}, you are {age} y.o. Great!")
    except ValueError:
        await message.answer("It should be a number!")
        message.next_step(lambda m: ask_age(m, name))

bot.run()
