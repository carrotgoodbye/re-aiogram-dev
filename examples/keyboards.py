from re_aiogram import Bot, Message
from re_aiogram.filters import Command
from re_aiogram.keyboard import SimpleKeyboard

bot = Bot(env_token="API_TOKEN")


@bot.message(Command("inline_keyboard_rows"))
async def inline_keyboard_rows(message: Message):
    kb = (
        SimpleKeyboard.inline()
        .row(
            ("👤 Profile", "profile"),
            ("⚙ Settings", "settings")
        )
        .row(
            ("❌ Close", "close")
        )
    )

    await message.answer(
        "Inline keyboard example",
        reply_markup=kb()
    )


@bot.message(Command("inline_keyboard_adjust"))
async def inline_keyboard_adjust(message: Message):
    kb = (
        SimpleKeyboard.inline()
        .buttons(
            ("One", "1"),
            ("Two", "2"),
            ("Three", "3"),
            ("Four", "4"),
            adjust=2
        )
    )

    await message.answer(
        "Inline keyboard example",
        reply_markup=kb()
    )


@bot.message(Command("reply_keyboard_rows"))
async def reply_keyboard_rows(message: Message):
    kb = (
        SimpleKeyboard.reply()
        .row("👤 Profile", "⚙ Settings")
        .row("❌ Close")
    )

    await message.answer(
        "Reply keyboard example",
        reply_markup=kb()
    )


@bot.message(Command("reply_keyboard_adjust"))
async def reply_keyboard_adjust(message: Message):
    kb = (
        SimpleKeyboard.reply(resize_keyboard=False)
        .buttons(
            "One",
            "Two",
            "Three",
            "Four",
            adjust=2
        )
    )

    await message.answer(
        "Reply keyboard example",
        reply_markup=kb()
    )


@bot.message(Command("clear_keyboard"))
async def clear_keyboard(message: Message):
    kb = SimpleKeyboard.reply().clear()

    await message.answer(
        "Reply keyboard cleared",
        reply_markup=kb()
    )


bot.run()
