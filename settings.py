# BOT FILES
commands_table_name = "tables/commands"
settings_table_name = "tables/settings"
user_levels_table_name = "tables/user_levels"
log_file = "log.txt"
debug_log_file_name = "discord.log"

# BOT SETTINGS
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
message_event_no_param = "I need a Pokemon name to look up events for!"
message_event_invalid_param = "Result number should be 1 or higher"
message_event_result_error = "Result number wasn't in the range of results ({})"
message_event_no_result = "Could not find an event with the Pokemon '{}'"
types_table = "shuffle_tables/types"
message_week_invalid_param = "There are {} weeks of events in the event rotation, so I need a number from 1 to {}"
num_weeks = 24
sm_rewards_table = "shuffle_tables/sm_rewards"
message_skill_no_param = "I need a Skill name to look up!"
message_skill_no_result = "Could not find a Skill entry with the name '{}'"
skill_notes_table = "shuffle_tables/skill_notes"
message_query_invalid_param = "Sorry, I didn't recognize any of those filters"
message_query_result = "Found {} Pokemon with {} (sorted by {})"
message_pokemon_no_param = "I need a Pokemon name to look up!"
message_pokemon_no_result = "Could not find a Pokemon entry with the name '{}'"
message_ap_no_param = "I need a BP and (optionally) a level"
message_ap_invalid_param = "BP should be a multiple of 10 between 30 and 90"
message_ap_invalid_param_2 = "Level should be an integer between 1 and 30"
ap_table = "shuffle_tables/ap"
message_exp_no_param = "I need a BP and either one target level or two levels"
message_exp_invalid_param = "BP should be a multiple of 10 between 30 and 90"
exp_table = "shuffle_tables/exp"
message_exp_result_3 = "EXP table for {} BP (Total EXP)"
message_exp_result_4 = "EXP table for {} BP (EXP from previous level)"
message_exp_invalid_param_2 = "Level should be an integer between 1 and 30"
message_exp_result = (
    "A {} BP Pokemon needs {} EXP to get from Level {} (AP {}) to Level {} (AP {})"
)
message_exp_result_2 = (
    "{} ({} BP) needs {} EXP to get from Level {} (AP {}) to Level {} (AP {})"
)
message_type_no_param = "I need a Type to look up!"
message_type_invalid_param = "That's not a valid type"
message_eb_rewards_no_result = (
    "Could not find an Escalation Battles with the Pokemon '{}'"
)
message_remind_me_status = (
    "You are signed up to be reminded for:\nWeeks: {}\nPokémon: {}"
)
message_remind_me_pokemon_success = (
    "Okay, you’re signed up to be reminded when {} appears in an event"
)
message_remind_me_pokemon_exists = "You already signed up for this Pokémon"
message_remind_me_week_exists = "You already signed up for this rotation week"
message_remind_me_week_success = (
    "Okay, you’re signed up to be reminded when rotation week {} starts"
)
message_unremind_me_no_param = "I need a week number or a Pokémon name"
message_unremind_me_week_non_exists = "You aren’t signed up for this rotation week"
message_unremind_me_week_success = (
    "Okay, you’re no longer signed up to be reminded when rotation week {} starts"
)
message_unremind_me_pokemon_non_exists = "You aren’t signed up for this Pokémon"
message_unremind_me_pokemon_success = (
    "Okay, you’re no longer signed up to be reminded when {} appears in an event"
)
custom_responses_table_name = "tables/custom_responses"
help_messages_table_name = "shuffle_tables/help_messages"
main_server_id = 0
message_dp_no_param = "I need a Disruption Pattern index to look up!"
message_dp_invalid_param = (
    "Disruption Pattern index should be a multiple of 6 from {} to {}"
)
disruption_patterns_min_index = 0
disruption_patterns_max_index = 7260
message_drain_list_no_param = "message_drain_list_no_param"
message_drain_list_invalid_param = (
    "One of the arguments wasn't an integer greater than 0"
)
message_drain_list_invalid_param_2 = "Moves has a limit of 55"
er_start_year = 2018
er_start_month = 2
er_start_day = 13
er_start_hour = 6
message_update_setting_success = "Updated {} from {} to {}"
message_update_setting_failed = (
    "That setting name doesn't seem to exist or you don't have permission to edit it"
)
message_add_setting_success = "Successfully added setting"
message_add_setting_failed = "That setting name already exists"
message_remove_setting_success = "Successfully removed setting"
message_remove_setting_failed = (
    "That setting name doesn't seem to exist or you don't have permission to edit it"
)
message_no_mentioned_user = "I need exactly one mentioned user!"
message_restrict_failed = "That user is already restricted"
message_restrict_failed_2 = "{} admins cannot be restricted"
message_restrict_success = "<@!{}> is now restricted from using {} commands"
message_unrestrict_failed = "That user is not restricted"
message_unrestrict_success = "<@!{}> is now unrestricted from using {} commands"
message_add_response_failed = (
    "That trigger message already has a custom response message"
)
message_add_response_success = "Added a custom response: '{}' -> '{}'"
message_remove_response_failed = (
    "'{}' doesn't seem to have a corresponding custom response"
)
message_remove_response_success = "Removed a custom response"
message_change_nickname_failed = "Cannot change nickname outside of a server"
message_add_requestable_roles_no_role = "I need a role to add"
requestable_roles_table_name = "tables/requestable_roles"
message_add_requestable_roles_success = "Roles added"
message_remove_requestable_roles_no_role = "I need a role to add"
message_remove_requestable_roles_success = "Roles removed"
bot_name = ""
message_oops_success = "Deleted last output from this user"
message_oops_failed = "No last output from this user to delete"
message_roll_result = "{} rolls {} point(s)"
message_request_roles_no_guild = "This command only works in a server"
message_request_roles_no_roles = (
    "Looks like there are no requestable roles in this server"
)
message_request_roles_wrong_user = "This interaction is serving someone else. You should run the command yourself to request roles."
message_request_roles_add_role_success = "Added {} role"
message_request_roles_add_role_failed = "Failed to add {} role"
message_request_roles_remove_role_success = "Removed {} role"
message_request_roles_remove_role_failed = "Failed to remove {} role"
message_request_roles_start = "Select a role to assign or unassign"
message_request_roles_finished = "All done"
message_no_mentioned_user_2 = "I need exactly zero or one mentioned user!"
roll_default_max = 7260
message_refresh_settings_success = "Settings refreshed"
message_refresh_app_commands_success = "App commands refreshed successfully"
message_add_admin_failed = "That user is already an admin"
message_add_admin_success = "<@!{}> is now an admin!"
message_remove_admin_failed = "That user is not an admin"
message_remove_admin_success = "<@!{}> is no longer an admin"
message_purge_invalid_param = (
    "Please give me an integer number of bot messages to purge"
)
purge_search_limit = 100
message_submit_comp_score_no_param = (
    "I need a Competitive Stage Pokemon, a score, and an attached image"
)
message_submit_comp_score_no_result = (
    "That Pokemon doesn’t seem to have a Competitive Stage"
)
message_submit_comp_score_invalid_param = "Score doesn’t seem to be valid"
message_submit_comp_score_success = "Successfully added competition score"
comp_verify_level = 2
comp_leaderboard_size_max = 10
comp_leaderboard_size_default = 5
message_leaderboard_no_param = "I need a Competitive Stage Pokemon"
message_leaderboard_no_result = "That Pokemon doesn’t seem to have a Competitive Stage"
message_leaderboard_no_submissions = "No submissions found"
message_user_comp_no_submissions = "No submission found"
