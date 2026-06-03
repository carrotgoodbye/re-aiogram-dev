from re_aiogram import Bot, Message
from re_aiogram.filters import F
from re_aiogram.types import MediaGroup

bot = Bot(env_token="API_TOKEN")


@bot.message(F.media_group_id)
async def album(
    message: Message,
    media_group: MediaGroup
):
    await message.answer(
        f"Album contains {media_group.count} items"
    )

    if media_group.caption:
        await message.answer(
            f"Caption: {media_group.caption}"
        )


bot.run()
