# re_aiogram

**re_aiogram** is a lightweight wrapper over [aiogram 3.x](https://aiogram.dev/) that keeps the familiar aiogram API while simplifying bot development and adding extra features.

The goal of the project is to stay fully compatible with aiogram, but provide a cleaner and more convenient developer experience.

---

# Install

```bash
pip install re_aiogram
```

```python
import re_aiogram
```

---

# Features

* familiar aiogram-style API
* simplified bot startup without explicit dispatcher
* router auto-loading
* built-in MediaGroup support
* aiogram-compatible imports
* simple and intuitive keyboard builder
* next_step handler registration (telebot-style)

---

# Quick Start

```python
from re_aiogram import Bot, Message
from re_aiogram.filters import Command

bot = Bot(token="YOUR_API_TOKEN")


@bot.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Hi! I am a Telegram bot powered by re_aiogram!"
    )


bot.run(logging_enabled=True)
```

You can specify a token from the virtual environment:

```python
bot = Bot(env_token="API_TOKEN")
```

---

# Next Step

A lightweight mechanism for step-by-step conversations without FSM. The next message from the user is intercepted and passed to the specified function.

## How it works

- `next_step` registers a function that will be called on the user's next message
- After calling, the function is automatically removed from the queue (one-shot)
- To continue the chain, call `next_step` again inside the function
- Works on a high-priority filter, so it intercepts the message before regular handlers

## Usage options

### 1. Via bot object
```python
bot.next_step(message, func)
bot.next_step(message.from_user.id, func) # alternative

bot.cancel_next_step(message)
bot.cancel_next_step(user_id) # alternative
```

### 2. Via message object
```python
message.next_step(func)
```

## Example

```python
from re_aiogram import Bot, Message
from re_aiogram.filters import Command

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
```

---

# SimpleKeyboard

`SimpleKeyboard` provides a fast and intuitive way to create inline and reply keyboards with minimal boilerplate.

```python
from re_aiogram.keyboard import SimpleKeyboard
```

## Inline keyboard

```python
@bot.message(Command("inline_keyboard"))
async def inline_keyboard(message: Message):
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
        "Inline keyboard",
        reply_markup=kb()
    )
```

You can also automatically arrange buttons using `adjust`:

```python
kb = (
    SimpleKeyboard.inline()
    .buttons(
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        adjust=2
    )
)
```

## Reply keyboard

```python
@bot.message(Command("reply_keyboard"))
async def reply_keyboard(message: Message):
    kb = (
        SimpleKeyboard.reply(resize_keyboard=True)
        .row("👤 Profile", "⚙ Settings")
        .row("❌ Close")
    )

    await message.answer(
        "Reply keyboard",
        reply_markup=kb()
    )
```

## Clear keyboard

```python
@bot.message(Command("clear_keyboard"))
async def clear_keyboard(message: Message):
    kb = (
        SimpleKeyboard.reply()
        .clear()
    )

    await message.answer(
        "Reply keyboard was removed",
        reply_markup=kb()
    )
```

---

# MediaGroup Handler

Built-in support for Telegram media groups.

```python
from re_aiogram import Bot, Message
from re_aiogram.filters import F
from re_aiogram.types import MediaGroup

bot = Bot(token="YOUR_API_TOKEN")


@bot.message(F.media_group_id)
async def handle_album(message: Message, media_group: MediaGroup):
    await message.answer_media_group(media_group)
```

`media_group` contains the collected media group messages.

## Properties

| Property                | Description                                                                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `media_group.count`     | Returns the number of media items in the group.                                                                                        |
| `media_group.caption`   | Returns the first caption found in the group (Telegram sends caption only on the first item). Returns `None` if no caption is present. |
| `media_group.captions`  | Returns a list of all captions from the group.                                                                                         |
| `media_group.messages`  | Returns a copy of the original `Message` objects from the group.                                                                       |
| `media_group.photos`    | Returns a list of `Message` objects that contain photos.                                                                               |
| `media_group.videos`    | Returns a list of `Message` objects that contain videos.                                                                               |
| `media_group.documents` | Returns a list of `Message` objects that contain documents.                                                                            |
| `media_group.audio`     | Returns a list of `Message` objects that contain audio files.                                                                          |
| `media_group.is_mixed`  | Returns `True` if the album contains different media types (e.g. photos and videos together).                                         |

---

# Routers

Router connection is simplified with `bot.load()`

### Project structure

```text
project/
│
├── main.py
└── handlers/
    └── start.py
```

### main.py

```python
from re_aiogram import Bot

bot = Bot(token="YOUR_API_TOKEN")

bot.load("handlers.start")

bot.run(logging_enabled=True)
```

### handlers/start.py

```python
from re_aiogram import Router, Message
from re_aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Router connected!")
```

---

# Future improvements

These features are planned for upcoming versions and are not yet part of the core API.

##### Flow System (FSM alternative)

A lightweight state/flow system replacing traditional FSM:

* step-based flow control
* `self.next()` and `self.finish()`
* shared data via class attributes
* simple chain-based conversation handling

## Example concept:

```python
from re_aiogram import Bot, Message
from re_aiogram.filters import Command
from re_aiogram.flow import Flow, start, step, finish

bot = Bot(token="YOUR_API_TOKEN")

class Register(Flow):
    name: str
    age: int

    @start()
    async def ask_name(self, message: Message):
        await message.answer("What is your name?")
        return self.next(self.ask_age, save="name", cast=lambda m: m.text)

    @step()
    async def ask_age(self, message: Message):
        await message.answer("How old are you?")
        return self.next(self.finish, save="age", cast=lambda m: int(m.text))

    @finish()
    async def finish(self, message: Message):
        await message.answer(f"{self.name}, {self.age} years old")

@bot.message(Command("register"), FlowEntry(Register))
async def register_cmd(message: Message):
    pass

bot.run()
```

---

# Philosophy

re_aiogram tries to make Telegram bot development:

* simpler
* cleaner
* less boilerplate-heavy
* more beginner-friendly

while still preserving compatibility with the `aiogram` ecosystem.