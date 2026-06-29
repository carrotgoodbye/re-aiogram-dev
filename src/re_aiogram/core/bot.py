from aiogram import Bot as _Bot, Dispatcher as _Dispatcher
from aiogram.types import Message
from aiogram import BaseMiddleware
import asyncio
import logging
import signal
import sys
import importlib
import os
from dotenv import load_dotenv


class Bot:
    """
    Bot class.
    """

    # Methods from aiogram.Bot
    _BOT_METHODS = frozenset({
        "send_message",
        "send_photo",
        "send_video",
        "send_audio",
        "send_document",
        "send_animation",
        "send_voice",
        "send_video_note",
        "send_media_group",
        "send_location",
        "send_venue",
        "send_contact",
        "send_poll",
        "send_dice",
        "send_chat_action",
        "send_sticker",
        "get_file",
        "get_file_url",
        "download_file",
        "get_me",
        "get_chat",
        "get_chat_member",
        "get_chat_member_count",
        "get_chat_administrators",
        "ban_chat_member",
        "unban_chat_member",
        "restrict_chat_member",
        "promote_chat_member",
        "set_chat_permissions",
        "set_chat_title",
        "set_chat_description",
        "set_chat_photo",
        "delete_chat_photo",
        "pin_chat_message",
        "unpin_chat_message",
        "unpin_all_chat_messages",
        "leave_chat",
        "answer_callback_query",
        "answer_inline_query",
        "edit_message_text",
        "edit_message_caption",
        "edit_message_media",
        "edit_message_reply_markup",
        "delete_message",
        "delete_messages",
        "forward_message",
        "copy_message",
        "copy_messages",
        "create_invoice_link",
        "send_invoice",
        "answer_shipping_query",
        "answer_pre_checkout_query",
        "set_my_commands",
        "delete_my_commands",
        "get_my_commands",
        "set_my_default_administrator_rights",
        "get_my_default_administrator_rights",
        "set_chat_menu_button",
        "get_chat_menu_button",
        "set_webhook",
        "delete_webhook",
        "get_webhook_info",
        "get_updates",
        "close",
        "session",
        "token",
    })

    def __init__(self, token: str = None, env_token: str | None = None):
        # token
        if token:
            self._token = token
        elif env_token:
            load_dotenv()
            self._token = os.getenv(env_token)
            if not self._token:
                raise ValueError(f"Environment variable '{env_token}' not found or empty")
        else:
            raise ValueError("Token is required: pass 'token' or 'env_token'")

        self._bot = _Bot(token=self._token)
        self._dp = _Dispatcher()

        # next_step storage: {user_id: func}
        self._next_steps: dict[int, callable] = {}

        # Register next_step handler FIRST — before any user handlers
        self._dp.message.register(
            self._handle_next_step,
            self._NextStepFilter(self)
        )

        # middlewares
        from .mediagroup import AlbumMiddleware
        self._dp.message.middleware(AlbumMiddleware())

        # Attach bot methods to message for convenient API
        self._dp.message.middleware(self._BotReferenceMiddleware(self))

    def __getattr__(self, name: str):
        if name in self._BOT_METHODS:
            return getattr(self._bot, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    @property
    def message(self):
        return self._dp.message

    @property
    def edited_message(self):
        return self._dp.edited_message

    @property
    def channel_post(self):
        return self._dp.channel_post

    @property
    def edited_channel_post(self):
        return self._dp.edited_channel_post

    @property
    def inline_query(self):
        return self._dp.inline_query

    @property
    def chosen_inline_result(self):
        return self._dp.chosen_inline_result

    @property
    def callback_query(self):
        return self._dp.callback_query

    @property
    def shipping_query(self):
        return self._dp.shipping_query

    @property
    def pre_checkout_query(self):
        return self._dp.pre_checkout_query

    @property
    def poll(self):
        return self._dp.poll

    @property
    def poll_answer(self):
        return self._dp.poll_answer

    @property
    def my_chat_member(self):
        return self._dp.my_chat_member

    @property
    def chat_member(self):
        return self._dp.chat_member

    @property
    def chat_join_request(self):
        return self._dp.chat_join_request

    @property
    def error(self):
        return self._dp.error

    # aiogram 3.7+ / Bot API 7.0+
    @property
    def business_connection(self):
        return self._dp.business_connection

    @property
    def business_message(self):
        return self._dp.business_message

    @property
    def deleted_business_messages(self):
        return self._dp.deleted_business_messages

    @property
    def message_reaction(self):
        return self._dp.message_reaction

    @property
    def message_reaction_count(self):
        return self._dp.message_reaction_count

    @property
    def purchased_paid_media(self):
        return self._dp.purchased_paid_media

    @property
    def chat_boost(self):
        return self._dp.chat_boost

    @property
    def removed_chat_boost(self):
        return self._dp.removed_chat_boost

    def next_step(self, target: Message | int, func: callable):
        """
        Register next handler for specific user.
        Next message from this user will be handled by `func` instead of regular handlers.

        :param target: Message object or user_id int
        :param func: async function(message) to call on next message
        """
        if isinstance(target, Message):
            user_id = target.from_user.id
        else:
            user_id = target
        self._next_steps[user_id] = func

    def cancel_next_step(self, target: Message | int):
        """
        Cancel registered next step for user.
        """
        if isinstance(target, Message):
            user_id = target.from_user.id
        else:
            user_id = target
        self._next_steps.pop(user_id, None)

    async def _handle_next_step(self, message: Message):
        """
        Internal handler that catches messages with a registered next_step.
        """
        user_id = message.from_user.id
        next_func = self._next_steps.pop(user_id, None)
        if next_func:
            try:
                return await next_func(message)
            except Exception as e:
                logging.exception("Error in next_step handler: %s", e)
                await message.answer("Произошла ошибка. Попробуйте снова.")

    class _NextStepFilter:
        """
        Filter that passes only when user has a pending next_step.
        """

        def __init__(self, bot_instance):
            self.bot = bot_instance

        def __call__(self, message: Message) -> bool:
            return message.from_user.id in self.bot._next_steps

    class _BotReferenceMiddleware(BaseMiddleware):
        """
        Middleware that attaches next_step and cancel_next_step methods
        directly to the Message instance for convenient API.
        """

        def __init__(self, bot_instance):
            self.bot = bot_instance

        async def __call__(self, handler, event, data):
            if isinstance(event, Message):
                # Bypass pydantic frozen check using object.__setattr__
                object.__setattr__(
                    event,
                    "next_step",
                    lambda func, msg=event: self.bot.next_step(msg, func)
                )
                object.__setattr__(
                    event,
                    "cancel_next_step",
                    lambda msg=event: self.bot.cancel_next_step(msg)
                )
            return await handler(event, data)

    def load(self, *paths: str):
        """
        Load routers from the specified paths.

        :param paths:
        """
        routers = []
        for path in paths:
            module = importlib.import_module(path)
            if hasattr(module, "router"):
                routers.append(module.router)
            else:
                raise ValueError(f"There is no 'router' variable in the {path} module")
        for router in routers:
            if router.parent_router is None:
                self._dp.include_router(router)

    def run(self, logging_enabled: bool = True):
        """
        Start the Bot with graceful shutdown.
        """
        if logging_enabled:
            logging.basicConfig(level=logging.INFO)
        try:
            asyncio.run(self._start())
        except (KeyboardInterrupt, SystemExit):
            logging.info("Bot stopped.")
        except Exception as e:
            logging.error("Polling error: %s", e)
            sys.exit(1)

    async def _start(self):
        """Start polling and ensure cleanup on exit."""
        loop = asyncio.get_running_loop()

        # Register signal handlers for graceful shutdown where supported
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._request_shutdown)
            except (NotImplementedError, ValueError):
                break
        try:
            await self._dp.start_polling(self._bot)
        finally:
            await self._shutdown() # sixsevenn

    def _request_shutdown(self):
        """Signal handler: initiate graceful stop."""
        logging.debug("Shutdown signal received, stopping polling...")
        asyncio.create_task(self._dp.stop_polling())

    async def _shutdown(self):
        """Close sessions and clean up resources."""
        logging.debug("Closing bot session...")
        await self._bot.session.close()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.remove_signal_handler(sig)
            except (NotImplementedError, ValueError):
                pass
