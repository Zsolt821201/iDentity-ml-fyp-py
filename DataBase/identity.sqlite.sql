BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Location" (
	"id"	INTEGER,
	"address"	TEXT,
	"description"	TEXT,
	"email"	TEXT UNIQUE,
	"name"	TEXT UNIQUE,
	"telephone"	TEXT UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "LocationPermission" (
	"locationId"	INTEGER,
	"userAccountId"	INTEGER,
	FOREIGN KEY("userAccountId") REFERENCES "UserAccount"("id"),
	FOREIGN KEY("locationId") REFERENCES "Location"("id"),
	PRIMARY KEY("locationId","userAccountId")
);
CREATE TABLE IF NOT EXISTS "Roster" (
	"id"	INTEGER,
	"locationId"	INTEGER,
	"signInDateTime"	TEXT,
	"signOutDateTime"	TEXT,
	"userAccountId"	INTEGER,
	FOREIGN KEY("userAccountId") REFERENCES "UserAccount"("id"),
	FOREIGN KEY("locationId") REFERENCES "Location"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Role" (
	"id"	INTEGER,
	"name"	TEXT UNIQUE,
	"desription"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO "Role" VALUES(1,'Administrator','Administrator');
INSERT INTO "Role" VALUES(2,'Manager','Manager');
INSERT INTO "Role" VALUES(3,'Employee','Employee');
INSERT INTO "Role" VALUES(4,'Visitor','Visitor');

CREATE TABLE IF NOT EXISTS "UserAccount" (
	"id"	INTEGER,
	"email"	TEXT UNIQUE,
	"enabled"	INTEGER,
	"faceRecognitionEnabled"	INTEGER,
	"firstName"	TEXT,
	"isTwin"	NUMERIC,
	"lastName"	TEXT,
	"password"	TEXT,
	"telephone"	TEXT UNIQUE,
	"username"	TEXT UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO "UserAccount" VALUES(1, "", 1, 0, "Admin", 0, "Admin", "admin", "", "admin");

CREATE TABLE IF NOT EXISTS "UserAccountRole" (
	"userAccountId"	INTEGER,
	"roleId"	INTEGER,
	FOREIGN KEY("userAccountId") REFERENCES "UserAccount"("id"),
	FOREIGN KEY("roleId") REFERENCES "Role"("id"),
	PRIMARY KEY("userAccountId","roleId")
);
COMMIT;
