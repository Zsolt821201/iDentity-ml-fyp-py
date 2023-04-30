
# Migration model changes example

```bash
>  python manage.py makemigrations identity

Did you rename locationpermission.location_id to locationpermission.location (a ForeignKey)? [y/N] y
Did you rename locationpermission.user_account_id to locationpermission.user_account (a ForeignKey)? [y/N] y
Did you rename roster.location_id to roster.location (a ForeignKey)? [y/N] y
Did you rename roster.user_account_id to roster.user_account (a ForeignKey)? [y/N] y
Migrations for 'identity':
  identity\migrations\0002_auto_20230211_1613.py
    - Rename field location_id on locationpermission to location
    - Rename field user_account_id on locationpermission to user_account
    - Rename field location_id on roster to location
    - Rename field user_account_id on roster to user_account
PS > python manage.py sqlmigrate identity 0002
BEGIN;
--
-- Rename field location_id on locationpermission to location
--
CREATE TABLE "new__identity_locationpermission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "location_id" integer NOT NULL REFERENCES "identity_location" ("id") DEFERRABLE INITIALLY DEFERRED, "user_account_id_id" bigint NOT NULL REFERENCES "identity_useraccount" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__identity_locationpermission" ("id", "user_account_id_id", "location_id") SELECT "id", "user_account_id_id", "location_id_id" FROM "identity_locationpermission";
DROP TABLE "identity_locationpermission";
ALTER TABLE "new__identity_locationpermission" RENAME TO "identity_locationpermission";
CREATE INDEX "identity_locationpermission_location_id_ee1c30d1" ON "identity_locationpermission" ("location_id");
CREATE INDEX "identity_locationpermission_user_account_id_id_e0f155b2" ON "identity_locationpermission" ("user_account_id_id");
--
-- Rename field user_account_id on locationpermission to user_account
--
CREATE TABLE "new__identity_locationpermission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "location_id" integer NOT NULL REFERENCES "identity_location" ("id") DEFERRABLE INITIALLY DEFERRED, "user_account_id" bigint NOT NULL REFERENCES "identity_useraccount" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__identity_locationpermission" ("id", "location_id", "user_account_id") SELECT "id", "location_id", "user_account_id_id" FROM "identity_locationpermission";
DROP TABLE "identity_locationpermission";
ALTER TABLE "new__identity_locationpermission" RENAME TO "identity_locationpermission";
CREATE INDEX "identity_locationpermission_location_id_ee1c30d1" ON "identity_locationpermission" ("location_id");
CREATE INDEX "identity_locationpermission_user_account_id_f6a45e09" ON "identity_locationpermission" ("user_account_id");
--
-- Rename field location_id on roster to location
--
CREATE TABLE "new__identity_roster" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sign_in_date" datetime NOT NULL, "sign_out_date" datetime NULL, "user_account_id_id" bigint NOT NULL REFERENCES "identity_useraccount" ("id") DEFERRABLE INITIALLY DEFERRED, "location_id" integer NOT NULL REFERENCES "identity_location" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__identity_roster" ("id", "sign_in_date", "sign_out_date", "user_account_id_id", "location_id") SELECT "id", "sign_in_date", "sign_out_date", "user_account_id_id", "location_id_id" FROM "identity_roster";
DROP TABLE "identity_roster";
ALTER TABLE "new__identity_roster" RENAME TO "identity_roster";
CREATE INDEX "identity_roster_user_account_id_id_d3d68cad" ON "identity_roster" ("user_account_id_id");
CREATE INDEX "identity_roster_location_id_0cb6dbc3" ON "identity_roster" ("location_id");
--
-- Rename field user_account_id on roster to user_account
--
CREATE TABLE "new__identity_roster" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sign_in_date" datetime NOT NULL, "sign_out_date" datetime NULL, "location_id" integer NOT NULL REFERENCES "identity_location" ("id") DEFERRABLE INITIALLY DEFERRED, "user_account_id" bigint NOT NULL REFERENCES "identity_useraccount" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__identity_roster" ("id", "sign_in_date", "sign_out_date", "location_id", "user_account_id") SELECT "id", "sign_in_date", "sign_out_date", "location_id", "user_account_id_id" FROM "identity_roster";
DROP TABLE "identity_roster";
ALTER TABLE "new__identity_roster" RENAME TO "identity_roster";
CREATE INDEX "identity_roster_location_id_0cb6dbc3" ON "identity_roster" ("location_id");
CREATE INDEX "identity_roster_user_account_id_f5249f37" ON "identity_roster" ("user_account_id");
COMMIT;
PS > python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, identity, sessions
Running migrations:
  Applying identity.0002_auto_20230211_1613... OK
```
