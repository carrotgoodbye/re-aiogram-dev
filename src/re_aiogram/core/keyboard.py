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

    def _make_button(self, button):
        """Convert various input formats to aiogram button objects."""
        if self.inline:
            # Already an InlineKeyboardButton
            if isinstance(button, InlineKeyboardButton):
                return button

            # Dict format: {"text": "...", "callback_data": "...", "url": "..."}
            if isinstance(button, dict):
                return InlineKeyboardButton(**button)

            # Tuple format: ("text", "callback_data")
            if isinstance(button, (tuple, list)):
                if len(button) >= 2:
                    kwargs = {"text": button[0], "callback_data": button[1]}
                    if len(button) >= 3 and isinstance(button[2], dict):
                        kwargs.update(button[2])
                    return InlineKeyboardButton(**kwargs)
                raise ValueError("Inline tuple must be at least (text, callback_data)")

            raise ValueError(f"Unsupported inline button format: {button}")

        else:
            # Already a KeyboardButton
            if isinstance(button, KeyboardButton):
                return button

            # Dict format: {"text": "...", "request_contact": True}
            if isinstance(button, dict):
                return KeyboardButton(**button)

            # String format: "text"
            if isinstance(button, str):
                return KeyboardButton(text=button)

            raise ValueError(f"Unsupported reply button format: {button}")

    def row(self, *buttons):
        row_buttons = [self._make_button(btn) for btn in buttons]
        self.builder.row(*row_buttons)
        return self

    def buttons(self, *buttons, adjust: int = None):
        for button in buttons:
            self.builder.add(self._make_button(button))

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