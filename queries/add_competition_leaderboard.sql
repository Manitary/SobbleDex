CREATE TABLE "competition_scores" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"user_id" INTEGER NOT NULL,
	"competition_pokemon" TEXT NOT NULL,
	"score" INTEGER NOT NULL,
	"message_id" INTEGER NOT NULL UNIQUE,
	"message_url" TEXT NOT NULL UNIQUE,
	"image_url" TEXT NOT NULL,
	"date" TEXT NOT NULL,
	"verified" INTEGER NOT NULL DEFAULT 0
)

INSERT INTO commands
    ("command_name", "module_name", "method_name", "command_type", "command_tier", "description")
VALUES
    ("leaderboard", "shuffle_commands", "competition_leaderboard", "prefix", 1, "Display the leaderboard for a competitive stage"),
	("deletecompscore", "shuffle_commands", "delete_own_comp_scores", "prefix", 1, "Delete one or more of the user's own submissions")
;

INSERT INTO settings
    ("key", "value")
VALUES
    ("comp_leaderboard_size_max", "10"),
    ("comp_leaderboard_size_default", "5"),
    ("message_leaderboard_no_param", "I need a Competitive Stage Pokemon"),
    ("message_leaderboard_no_result", "That Pokemon doesn’t seem to have a Competitive Stage"),
	("message_leaderboard_no_submissions", "No submission found"),
	("message_user_comp_no_submissions", "No submission found"),
	("message_user_delete_all_own_comp_scores", "ALL your competition submissions will be deleted. This action is irreversible. Are you sure?"),
	("message_success_delete_all_own_comp_scores", "{} submissions deleted"),
	("message_success_delete_own_comp_score", "Submission deleted"),
	("message_failed_delete_own_comp_score", "Invalid command. Either the URL is not a submission, or the submission does not exist in the database, or it is not your own submission")
;

UPDATE commands SET command_tier = 1 WHERE command_name = submitcompscore
UPDATE commands SET command_tier = 1 WHERE command_name = compscores
