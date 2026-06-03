from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove


class SimpleKeyboard:
    def __init__(
            self,
            inline: bool = True,
            resize_keyboard: bool = True
    ):
        self.inline = inline
        self.resize_keyboard = resize_keyboard

        if inline:
            self.builder = InlineKeyboardBuilder()
        else:
            self.builder = ReplyKeyboardBuilder()

    # FACTORIES

    @classmethod
    def inline(cls):
        return cls(inline=True)

    @classmethod
    def reply(cls, resize_keyboard: bool = True):
        return cls(
            inline=False,
            resize_keyboard=resize_keyboard
        )

    def row(self, *buttons):
        row_buttons = []

        for button in buttons:
            if self.inline:
                text, data = button
                row_buttons.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=data
                    )
                )
            else:
                text = button
                row_buttons.append(
                    KeyboardButton(
                        text=text
                    )
                )

        self.builder.row(*row_buttons)
        return self

    def buttons(self, *buttons, adjust: int = None):
        for button in buttons:
            if self.inline:
                text, data = button
                self.builder.add(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=data
                    )
                )
            else:
                text = button
                self.builder.add(
                    KeyboardButton(
                        text=text
                    )
                )

        if adjust:
            self.builder.adjust(adjust)

        return self

    def clear(self):
        return ReplyKeyboardRemove

    # BUILD

    def build(self):
        return self.builder.as_markup(
            resize_keyboard=(
                self.resize_keyboard
                if not self.inline
                else None
            )
        )

    def __call__(self):
        return self.build()
