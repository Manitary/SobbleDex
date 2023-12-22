import itertools
import re
from typing import Any

import db
import settings
import utils
from koduck import KoduckContext
from models import Payload

from .decorators import min_param

RE_PING = re.compile(r"<@!?[0-9]*>")


@min_param(num=1, error=settings.message_list_aliases_no_param)
async def list_aliases(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    aliases = db.get_aliases()
    original = aliases.get(args[0].lower(), args[0])

    results = [k for k, v in aliases.items() if v.lower() == original.lower()]
    if not results:
        return Payload(content=settings.message_list_aliases_no_result)

    return Payload(
        content=settings.message_list_aliases_result.format(
            original, ", ".join(results)
        )
    )


@min_param(num=2, error=settings.message_add_alias_no_param)
async def add_alias(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    if len(args) > settings.manage_alias_limit + 1:
        return Payload(
            content=settings.message_add_alias_too_many_params.format(
                settings.manage_alias_limit
            )
        )

    aliases = db.get_aliases()
    original = aliases.get(args[0].lower(), args[0])
    new_aliases = utils.remove_duplicates(filter(None, args[1:]))

    bad_alias = list(filter(lambda x: bool(RE_PING.findall(x)), new_aliases))
    success, duplicate, failure = db.add_aliases(
        original, *(a for a in new_aliases if a not in bad_alias)
    )
    return_message = (
        "\n".join(
            itertools.chain(
                (
                    settings.message_add_alias_success.format(original, s)
                    for s in success
                ),
                (
                    settings.message_add_alias_failed.format(
                        d, aliases.get(d.lower(), original)
                    )
                    for d in duplicate
                ),
                (settings.message_add_alias_failed_2.format(f) for f in failure),
                (settings.message_add_alias_failed_3.format(b) for b in bad_alias),
            )
        )
        or settings.message_add_alias_failed_4
    )

    return Payload(content=return_message)


@min_param(num=1, error=settings.message_remove_alias_no_param)
async def remove_alias(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    if len(args) > settings.manage_alias_limit:
        return Payload(
            content=settings.message_remove_alias_too_many_params.format(
                settings.manage_alias_limit
            )
        )

    success, not_exist, failure = db.remove_aliases(*args)
    return_message = "\n".join(
        itertools.chain(
            (settings.message_remove_alias_success.format(*s) for s in success),
            (settings.message_remove_alias_failed.format(n) for n in not_exist),
            (settings.message_remove_alias_failed_2.format(f) for f in failure),
        )
    )

    return Payload(content=return_message)
