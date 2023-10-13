import importlib
import logging
import sys

import db
import settings
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

    if errors:
        print(errors)


# Background task is run every set interval while bot is running (by default every 10 seconds)
async def background_task(koduck_instance: Koduck) -> None:
    pass


settings.background_task = background_task

koduck = Koduck()
koduck.add_command("refreshcommands", refresh_commands, "prefix", 3)
if settings.enable_debug_logger:
    log_handler = logging.FileHandler(
        filename=settings.debug_log_file_name, encoding="utf-8", mode="w"
    )
    koduck.client.run(settings.token, log_handler=log_handler, log_level=logging.DEBUG)
else:
    koduck.client.run(settings.token, log_handler=None)
