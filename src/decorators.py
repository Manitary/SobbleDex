import functools
import urllib.parse
from typing import Any, Callable, Protocol

import discord

from koduck import KoduckContext
from models import Payload


class BotCommand(Protocol):
    async def __call__(
        self, context: KoduckContext, *args: str, **kwargs: Any
    ) -> discord.Message | Payload | None:
        ...


def min_param(num: int, error: str) -> Callable[[BotCommand], BotCommand]:
    """If the bot command receives less than ``num`` arguments, send the ``error`` message."""

    def decorator(func: BotCommand) -> BotCommand:
        async def wrapper(
            context: KoduckContext, *args: str, **kwargs: Any
        ) -> discord.Message | Payload | None:
            assert context.koduck
            if len(args) < num:
                return await context.koduck.send_message(
                    receive_message=context.message, content=error
                )
            return await func(context, *args, **kwargs)

        return wrapper

    return decorator


def allow_space_delimiter() -> Callable[[BotCommand], BotCommand]:
    """Make the command accept both comma- and space-delimited arguments."""

    def decorator(func: BotCommand) -> BotCommand:
        async def wrapper(
            context: KoduckContext, *args: str, **kwargs: Any
        ) -> discord.Message | Payload | None:
            if len(args) != 1:
                # Comma-separated arguments -> do nothing
                return await func(context, *args, **kwargs)
            temp = tuple(args[0].split())
            if len(temp) == 1:
                # No space separation -> do nothing
                return await func(context, *args, **kwargs)
            try:
                first_num = next(i for i, x in enumerate(temp) if x.isdigit())
                assert first_num > 0
            except StopIteration:
                # No element is a number -> do nothing
                pass
            except AssertionError:
                # The first element is a number -> split
                args = temp
            else:
                # Merge all arguments before the first number
                # (at least >=2 args due to previous assertion)
                args = ("".join(temp[:first_num]),) + temp[first_num:]

                if args[0].lower() == "zygarde" and args[1] in {"10", "50", "100"}:
                    # Special case with the only pokemon including a number in the name
                    args = (args[0] + args[1],) + args[2:]

            return await func(context, *args, **kwargs)

        return wrapper

    return decorator


url_encode = functools.partial(urllib.parse.quote, safe=":/")
