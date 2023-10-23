INSERT INTO commands
    ("command_name", "module_name", "method_name", "command_type", "command_tier", "description")
VALUES
    ("next", "shuffle_commands", "next_stage", "prefix", 1, "Query the next stage if the previous command requested a main or EX stage")
;

INSERT INTO settings
    ("key", "value")
VALUES
    ("message_last_query_not_stage", "Your previous query was not a main or EX stage"),
    ("message_last_query_error", "Unexpected error, contact my owner to investigate")
;
