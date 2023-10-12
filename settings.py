# BOT FILES
commands_table_name = "tables/commands"
settings_table_name = "tables/settings"
user_levels_table_name = "tables/user_levels"
log_file = "log.txt"
debug_log_file_name = "discord.log"

# BOT SETTINGS
token = ""
command_prefix = "/"
param_delim = " "
default_user_level = 1
max_user_level = 3
log_format = "{timestamp}\t{type}\t{server_id}\t{server_name}\t{channel_id}\t{channel_name}\t{user_id}\t{discord_tag}\t{nickname}\t{message_content}\t{data}\t{extra}"
channel_cooldown = 1000
ignore_cd_level = 2
user_cooldown_0 = 60000
user_cooldown_1 = 3000
output_history_size = 10
background_task = None
background_task_interval = 10
enable_debug_logger = False
enable_run_command = False
run_command_name = "run"
run_command_description = "Run a prefix command"
run_command_default_response = "Command ran successfully"

# MESSAGES
message_something_broke = "Something broke"
message_unknown_command = "Command not recognized"
message_unhandled_error = "Unhandled error ({})"
message_result_too_long = "Sorry, the result was too long to output ({}/{} characters)"
message_embed_too_long = "Sorry, the embed was too long to output ({} {}/{} characters)"
message_embed_empty_field = "The output embed was invalid ({} can't be empty)"
message_cooldown_active = "Cooldown active"
message_restricted_access = "You do not have permission to use this command"
message_missing_params = "Missing required parameters: {}"

# Miscellaneous
# Temporarily added manually for testing purposes
# Normally they are loaded from the settings.txt file
events_table = "shuffle_tables/events"
event_stages_table = "shuffle_tables/event_stages"
message_refresh_commands_success = "Commands refreshed successfully"
message_refresh_commands_errors = "There were some errors while refreshing commands:"
message_list_aliases_no_param = "I need a name to look for aliases for!"
message_list_aliases_no_result = "There are currently no aliases assigned to this name"
message_list_aliases_result = "'{}' is also known as: {}"
aliases_table = "shuffle_tables/aliases"
main_stages_table = "shuffle_tables/main_stages"
expert_stages_table = "shuffle_tables/expert_stages"
event_stages_table = "shuffle_tables/event_stages"
message_add_alias_no_param = "I need at least two parameters: original, alias(es)"
manage_alias_limit = 10
message_add_alias_too_many_params = "Please only give me up to {} aliases to add!"
message_add_alias_success = "Added an alias: '{}' is now also known as '{}'"
message_add_alias_failed = "'{}' is already used as an alias for '{}'"
message_add_alias_failed_2 = "Failed to add '{}' as an alias, please try again"
message_add_alias_failed_3 = "Failed to add `{}` as an alias because it contains a ping"
message_remove_alias_no_param = "I need an alias to remove!"
message_remove_alias_too_many_params = "Please only give me up to {} aliases to remove!"
message_remove_alias_success = "Removed an alias: '{}' is no longer known as '{}'"
message_remove_alias_failed = "'{}' is not currently assigned as an alias to anything"
message_remove_alias_failed_2 = "Failed to remove '{}' as an alias, please try again"
reminders_table = "shuffle_table/reminders"
message_reminder_week = "Rotation week {} has started!"
message_reminder_pokemon = "{} has appeared in an event!"
message_reminder_header = "<@!{}> Here are your reminders:\n{}"
message_stage_no_param = "I need a stage index/pokemon to look up!"
message_stage_invalid_param = "Result number should be 1 or higher"
message_stage_main_invalid_param = "Main Stages range from {} to {}"
main_stages_min_index = 1
main_stages_max_index = 700
message_stage_expert_invalid_param = "Expert Stages range from {} to {}"
expert_stages_min_index = 0
expert_stages_max_index = 52
message_stage_event_invalid_param = "Event Stages range from {} to {}"
event_stages_min_index = 0
event_stages_max_index = 715
eb_details_table = "shuffle_tables/eb_details"
message_stage_no_result = "Could not find a stage with the Pokemon '{}'"
message_stage_result_error = "Result number wasn't in the range of results ({})"
choice_react_limit = 9
message_stage_multiple_results = (
    "There were multiple results. Which one of these were you looking for?"
)
pokemon_table = "shuffle_tables/pokemon"
skills_table = "shuffle_tables/skills"
dym_limit = 5
dym_threshold = 0.7
message_pokemon_lookup_no_result = "Could not find the {} named '{}'"
message_pokemon_lookup_suggest = "Did you mean one of these?"
dym_timeout = 30
stage_notes_table = "shuffle_tables/stage_notes"
message_eb_invalid_param = "EB level should be 1 or higher"
message_eb_no_result = "Could not find an Escalation Battles with the Pokemon '{}'"
eb_rewards_table = "shuffle_tables/eb_rewards"
