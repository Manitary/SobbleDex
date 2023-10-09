CREATE TABLE "commands" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"command_name" TEXT UNIQUE NOT NULL,
	"module_name" TEXT NOT NULL,
	"method_name" TEXT NOT NULL,
	"command_type" TEXT NOT NULL,
	"command_tier" INTEGER NOT NULL,
	"description" TEXT DEFAULT ''
);

CREATE TABLE "custom_responses" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"message" TEXT UNIQUE NOT NULL,
	"response" TEXT NOT NULL
);

CREATE TABLE "settings" (
	"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"setting" TEXT UNIQUE NOT NULL,
	"value" TEXT NOT NULL,
	"tier" INTEGER DEFAULT NULL
);
