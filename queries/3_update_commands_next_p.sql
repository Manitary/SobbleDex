UPDATE settings
SET
    key = "message_last_query_invalid_stage",
    value = "The command only works with a main or EX stage"
WHERE
    key = "message_last_query_not_stage"
;

UPDATE settings
SET
    key = "message_no_previous_stage",
    value = "No stage in your recent query history"
WHERE
    key = "message_pokemon_last_query_not_stage"
;
