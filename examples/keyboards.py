from re_aiogram import Bot, Message
from re_aiogram.filters import Command
from re_aiogram.keyboard import SimpleKeyboard, InlineKeyboardButton

bot = Bot(env_token="API_TOKEN")


@bot.message(Command("inline_keyboard"))
async def inline_keyboard(message: Message):
    kb = (
        SimpleKeyboard.inline()
        .buttons(
            ("One", "1"),
            ("Two", "2"),
            ("Three", "3"),
            ("Four", "4"),
            ("Five", "5"),
            ("Six", "6"),
            adjust=3
        )

        # You can generate buttons from tuple (text, callback_data)
        .row(
            ("👤 Profile", "profile"),
            ("⚙ Settings", "settings")
        )

        # From aiogram objects
        .row(
            InlineKeyboardButton(text="❌ Close", callback_data="delete", style="danger")
        )

        # From dict
        .row(
            {
                "text": "❌ Close",
                "callback_data": "delete",
                "style": "danger"
            }
        )
    )

    await message.answer(
        "Inline keyboard example",
        reply_markup=kb()
    )


@bot.message(Command("reply_keyboard"))
async def reply_keyboard(message: Message):
    kb = (
        SimpleKeyboard.reply()
        .buttons(
            ("One", "1"),
            ("Two", "2"),
            ("Three", "3"),
            ("Four", "4"),
            ("Five", "5"),
            ("Six", "6"),
            adjust=3
        )
        .row("👤 Profile", "⚙ Settings")
        .row(
            {
                "text": "❌ Close",
                "style": "danger"
            }
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
