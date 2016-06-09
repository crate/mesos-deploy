CREATE TABLE IF NOT EXISTS "doc"."nyc" (
   "closed_date" timestamp,
   "created_date" timestamp,
   "due_date" timestamp,
   "latitude" float,
   "longitude" float,
   "resolution_action_updated_date" timestamp,
   "unique_key" STRING,
   "geometry" geo_point,
   PRIMARY KEY ("unique_key")
);
