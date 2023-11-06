CREATE TABLE "aliases" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"alias" TEXT UNIQUE NOT NULL,
	"original_name" TEXT NOT NULL
);

CREATE TABLE "ap" (
	"base_ap" INTEGER NOT NULL PRIMARY KEY,
	"lvl1" INTEGER NOT NULL,
	"lvl2" INTEGER NOT NULL,
	"lvl3" INTEGER NOT NULL,
	"lvl4" INTEGER NOT NULL,
	"lvl5" INTEGER NOT NULL,
	"lvl6" INTEGER NOT NULL,
	"lvl7" INTEGER NOT NULL,
	"lvl8" INTEGER NOT NULL,
	"lvl9" INTEGER NOT NULL,
	"lvl10" INTEGER NOT NULL,
	"lvl11" INTEGER NOT NULL,
	"lvl12" INTEGER NOT NULL,
	"lvl13" INTEGER NOT NULL,
	"lvl14" INTEGER NOT NULL,
	"lvl15" INTEGER NOT NULL,
	"lvl16" INTEGER NOT NULL,
	"lvl17" INTEGER NOT NULL,
	"lvl18" INTEGER NOT NULL,
	"lvl19" INTEGER NOT NULL,
	"lvl20" INTEGER NOT NULL,
	"lvl21" INTEGER NOT NULL,
	"lvl22" INTEGER NOT NULL,
	"lvl23" INTEGER NOT NULL,
	"lvl24" INTEGER NOT NULL,
	"lvl25" INTEGER NOT NULL,
	"lvl26" INTEGER NOT NULL,
	"lvl27" INTEGER NOT NULL,
	"lvl28" INTEGER NOT NULL,
	"lvl29" INTEGER NOT NULL,
	"lvl30" INTEGER NOT NULL
);

CREATE TABLE "eb_details" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"pokemon" TEXT NOT NULL,
	"start_level" INTEGER NOT NULL,
	"end_level" INTEGER NOT NULL,
	"stage_index" INTEGER NOT NULL
);

CREATE TABLE "eb_rewards" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"pokemon" TEXT NOT NULL,
	"level" INTEGER NOT NULL,
	"reward" INTEGER NOT NULL,
	"amount" INTEGER NOT NULL,
	"alternative" TEXT
);

CREATE TABLE "event_stages" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"pokemon" TEXT NOT NULL,
	"hp" INTEGER NOT NULL,
	"hp_mobile" INTEGER NOT NULL,
	"moves" INTEGER NOT NULL,
	"seconds" INTEGER NOT NULL,
	"exp" INTEGER NOT NULL,
	"base_catch" INTEGER NOT NULL,
	"bonus_catch" INTEGER NOT NULL,
	"base_catch_mobile" INTEGER NOT NULL,
	"bonus_catch_mobile" INTEGER NOT NULL,
	"default_supports" TEXT NOT NULL,
	"s_rank" INTEGER NOT NULL,
	"a_rank" INTEGER NOT NULL,
	"b_rank" INTEGER NOT NULL,
	"num_s_ranks_to_unlock" INTEGER NOT NULL DEFAULT 0,
	"is_puzzle_stage" TEXT DEFAULT "Normal",
	"extra_hp" INTEGER NOT NULL DEFAULT 0,
	"layout_index" INTEGER NOT NULL DEFAULT 0,
	"cost_type" TEXT NOT NULL,
	"attempt_cost" INTEGER NOT NULL,
	"drop_1_item" TEXT,
	"drop_1_amount" INTEGER,
	"drop_2_item" TEXT,
	"drop_2_amount" INTEGER,
	"drop_3_item" TEXT,
	"drop_3_amount" INTEGER,
	"drop_1_rate" FLOAT,
	"drop_2_rate" FLOAT,
	"drop_3_rate" FLOAT,
	"items_available" TEXT,
	"rewards" TEXT,
	"rewards_ux" TEXT,
	"cd1" TEXT,
	"cd2" TEXT,
	"cd3" TEXT
);

CREATE TABLE "main_stages" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"pokemon" TEXT NOT NULL,
	"hp" INTEGER NOT NULL,
	"hp_mobile" INTEGER NOT NULL,
	"moves" TEXT NOT NULL,
	"seconds" INTEGER NOT NULL DEFAULT 0,
	"exp" TEXT NOT NULL,
	"base_catch" INTEGER NOT NULL,
	"bonus_catch" INTEGER NOT NULL,
	"base_catch_mobile" INTEGER NOT NULL,
	"bonus_catch_mobile" INTEGER NOT NULL,
	"default_supports" TEXT NOT NULL,
	"s_rank" INTEGER NOT NULL,
	"a_rank" INTEGER NOT NULL,
	"b_rank" INTEGER NOT NULL,
	"num_s_ranks_to_unlock" INTEGER NOT NULL DEFAULT 0,
	"is_puzzle_stage" TEXT DEFAULT "Normal",
	"extra_hp" INTEGER NOT NULL DEFAULT 0,
	"layout_index" INTEGER NOT NULL DEFAULT 0,
	"cost_type" TEXT NOT NULL DEFAULT "Heart",
	"attempt_cost" INTEGER NOT NULL DEFAULT 1,
	"drop_1_item" TEXT,
	"drop_1_amount" INTEGER,
	"drop_2_item" TEXT,
	"drop_2_amount" INTEGER,
	"drop_3_item" TEXT,
	"drop_3_amount" INTEGER,
	"drop_1_rate" FLOAT,
	"drop_2_rate" FLOAT,
	"drop_3_rate" FLOAT,
	"items_available" TEXT,
	"rewards" TEXT,
	"rewards_ux" TEXT,
	"cd1" TEXT,
	"cd2" TEXT,
	"cd3" TEXT
);

CREATE TABLE "expert_stages" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"pokemon" TEXT NOT NULL,
	"hp" INTEGER NOT NULL,
	"hp_mobile" INTEGER NOT NULL,
	"moves" INTEGER NOT NULL DEFAULT 0,
	"seconds" INTEGER NOT NULL,
	"exp" INTEGER NOT NULL,
	"base_catch" INTEGER NOT NULL,
	"bonus_catch" INTEGER NOT NULL,
	"base_catch_mobile" INTEGER NOT NULL,
	"bonus_catch_mobile" INTEGER NOT NULL,
	"default_supports" TEXT NOT NULL,
	"s_rank" INTEGER NOT NULL,
	"a_rank" INTEGER NOT NULL,
	"b_rank" INTEGER NOT NULL,
	"num_s_ranks_to_unlock" INTEGER NOT NULL,
	"is_puzzle_stage" TEXT DEFAULT "Normal",
	"extra_hp" INTEGER NOT NULL DEFAULT 0,
	"layout_index" INTEGER NOT NULL DEFAULT 0,
	"cost_type" TEXT NOT NULL DEFAULT "Heart",
	"attempt_cost" INTEGER NOT NULL DEFAULT 1,
	"drop_1_item" TEXT,
	"drop_1_amount" INTEGER,
	"drop_2_item" TEXT,
	"drop_2_amount" INTEGER,
	"drop_3_item" TEXT,
	"drop_3_amount" INTEGER,
	"drop_1_rate" FLOAT,
	"drop_2_rate" FLOAT,
	"drop_3_rate" FLOAT,
	"items_available" TEXT,
	"rewards" TEXT,
	"rewards_ux" TEXT,
	"cd1" TEXT,
	"cd2" TEXT,
	"cd3" TEXT
);

CREATE TABLE "exp" (
	"base_ap" INTEGER NOT NULL PRIMARY KEY,
	"lvl0" INTEGER NOT NULL DEFAULT 0,
	"lvl1" INTEGER NOT NULL DEFAULT 0,
	"lvl2" INTEGER NOT NULL,
	"lvl3" INTEGER NOT NULL,
	"lvl4" INTEGER NOT NULL,
	"lvl5" INTEGER NOT NULL,
	"lvl6" INTEGER NOT NULL,
	"lvl7" INTEGER NOT NULL,
	"lvl8" INTEGER NOT NULL,
	"lvl9" INTEGER NOT NULL,
	"lvl10" INTEGER NOT NULL,
	"lvl11" INTEGER NOT NULL,
	"lvl12" INTEGER NOT NULL,
	"lvl13" INTEGER NOT NULL,
	"lvl14" INTEGER NOT NULL,
	"lvl15" INTEGER NOT NULL,
	"lvl16" INTEGER NOT NULL,
	"lvl17" INTEGER NOT NULL,
	"lvl18" INTEGER NOT NULL,
	"lvl19" INTEGER NOT NULL,
	"lvl20" INTEGER NOT NULL,
	"lvl21" INTEGER NOT NULL,
	"lvl22" INTEGER NOT NULL,
	"lvl23" INTEGER NOT NULL,
	"lvl24" INTEGER NOT NULL,
	"lvl25" INTEGER NOT NULL,
	"lvl26" INTEGER NOT NULL,
	"lvl27" INTEGER NOT NULL,
	"lvl28" INTEGER NOT NULL,
	"lvl29" INTEGER NOT NULL,
	"lvl30" INTEGER NOT NULL
);

CREATE TABLE "help_messages" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"message_type" TEXT NOT NULL,
	"message_text" TEXT NOT NULL
);

CREATE TABLE "pokemon" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"pokemon" TEXT NOT NULL UNIQUE,
	"dex" INTEGER NOT NULL,
	"type" TEXT NOT NULL,
	"bp" INTEGER NOT NULL,
	"rml" INTEGER NOT NULL DEFAULT 5,
	"max_ap" INTEGER NOT NULL,
	"skill" TEXT NOT NULL,
	"ss" TEXT,
	"icons" INTEGER NOT NULL DEFAULT 0,
	"msu" INTEGER DEFAULT 0,
	"mega_power" TEXT,
	"fake" INTEGER DEFAULT 0
);

CREATE TABLE "skill_notes" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"skill" TEXT NOT NULL UNIQUE,
	"notes" TEXT NOT NULL
);

CREATE TABLE "skills" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"skill" TEXT NOT NULL UNIQUE,
	"description" TEXT NOT NULL,
	"rate1" INTEGER NOT NULL,
	"rate2" INTEGER NOT NULL,
	"rate3" INTEGER NOT NULL,
	"type" TEXT NOT NULL,
	"multiplier" REAL NOT NULL,
	"bonus_effect" TEXT NOT NULL,
	"bonus1" REAL NOT NULL,
	"bonus2" REAL NOT NULL,
	"bonus3" REAL NOT NULL,
	"bonus4" REAL NOT NULL,
	"sp1" INTEGER NOT NULL,
	"sp2" INTEGER NOT NULL,
	"sp3" INTEGER NOT NULL,
	"sp4" INTEGER NOT NULL
);

CREATE TABLE "sm_rewards" (
	"level" INTEGER NOT NULL PRIMARY KEY,
	"first_reward_type" TEXT NOT NULL,
	"first_reward_amount" INTEGER NOT NULL,
	"repeat_reward_type" TEXT NOT NULL,
	"repeat_reward_amount" INTEGER NOT NULL
);

CREATE TABLE "stage_notes" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"stage_id" TEXT NOT NULL UNIQUE,
	"notes" TEXT NOT NULL
);

CREATE TABLE "types" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"type" TEXT NOT NULL UNIQUE,
	"se" TEXT,
	"nve" TEXT,
	"weak" TEXT,
	"resist" TEXT,
	"status_immune" TEXT
);

CREATE TABLE "events" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"stage_type" TEXT NOT NULL,
	"pokemon" TEXT NOT NULL,
	"stage_ids" TEXT NOT NULL,
	"repeat_type" TEXT NOT NULL,
	"repeat_param_1" INTEGER,
	"repeat_param_2" INTEGER,
	"date_start" TEXT,
	"date_end" TEXT,
	"duration" TEXT,
	"cost_unlock" TEXT,
	"notes" TEXT,
	"encounter_rates" TEXT	
);
