import datetime
import importlib
import logging
import sys

import dotenv
import pytz

import db
import settings
import utils
from koduck import Koduck, KoduckContext


# Required method to setup Koduck.
# Can also be run as a command after startup to update any manual changes to the commands table.
async def refresh_commands(context: KoduckContext) -> None:
    assert context.koduck
    errors: list[str] = []
    commands = list(db.get_commands())
    if commands:
        context.koduck.clear_commands()
        for command in commands:
            if command.module_name == "main":
                try:
                    context.koduck.add_command(
                        command.command_name,
                        globals()[command.method_name],
                        command.command_type,
                        command.command_tier,
                        command.description,
                    )
                except Exception as e:
                    errors.append(f"Failed to import command '{command}': `{e}`")
                continue

            if command.module_name not in sys.modules:
                try:
                    importlib.import_module(command.module_name)
                except Exception as e:
                    errors.append(
                        f"Failed to import module '{command.module_name}': `{e}`"
                    )
            try:
                context.koduck.add_command(
                    command.command_name,
                    getattr(sys.modules[command.module_name], command.method_name),
                    command.command_type,
                    command.command_tier,
                    command.description,
                )
            except Exception as e:
                errors.append(f"Failed to import command '{command}': `{e}`")

    if settings.enable_run_command:
        context.koduck.add_run_slash_command()

    if context.message:
        if errors:
            await context.koduck.send_message(
                context.message,
                content=settings.message_refresh_commands_errors
                + "\n"
                + "\n".join(errors),
            )
        else:
            await context.koduck.send_message(
                context.message, content=settings.message_refresh_commands_success
            )
        return

    for e in errors:
        print(e)


current_day = -1
current_week = -1


async def background_task(koduck: Koduck) -> None:
    global current_day
    global current_week
    current_time = datetime.datetime.now(tz=pytz.timezone("Etc/GMT+6"))

    if current_day == -1 or current_week == -1:
        current_day = current_time.day
        current_week = utils.get_current_week()
        return

    if current_time.day == current_day:
        return

    current_day = current_time.day
    current_week2 = utils.get_current_week()
    week_changed, current_week = current_week2 != current_week, current_week2
    event_pokemon = utils.get_current_event_pokemon()
    for reminder in db.get_reminders():
        reminder_strings: list[str] = []
        if week_changed and current_week in reminder.weeks:
            reminder_strings.append(settings.message_reminder_week.format(current_week))
        reminder_strings.extend(
            settings.message_reminder_pokemon.format(ep)
            for ep in event_pokemon
            if ep in reminder.pokemon
        )
        if reminder_strings:
            the_user = await koduck.client.fetch_user(reminder.user_id)
            await the_user.send(
                content=settings.message_reminder_header.format(
                    reminder.user_id, "\n".join(reminder_strings)
                )
            )


def main() -> None:
    config = dotenv.dotenv_values(".env")
    token = config.get("token", "")
    if not token:
        print("Token not configured")
        sys.exit(1)

    settings.background_task = background_task

    koduck = Koduck()
    koduck.add_command("refreshcommands", refresh_commands, "prefix", 3)
    if settings.enable_debug_logger:
        log_handler = logging.FileHandler(
            filename=settings.debug_log_file_name, encoding="utf-8", mode="w"
        )
        koduck.client.run(token, log_handler=log_handler, log_level=logging.DEBUG)
    else:
        koduck.client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
