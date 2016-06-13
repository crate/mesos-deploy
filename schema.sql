CREATE TABLE IF NOT EXISTS "doc"."nyc" (
  "closed_date" timestamp,
  "created_date" timestamp,
  "due_date" timestamp,
  "latitude" float,
  "longitude" float,
  "resolution_action_updated_date" timestamp,
  "geometry" geo_point,
  "month" as date_format('%Y-%c', created_date),
INDEX complaint_type_ft USING fulltext (complaint_type),
INDEX descriptor_ft USING fulltext (descriptor),
INDEX location_type_ft USING fulltext (location_type),
INDEX incident_address_ft USING fulltext (incident_address),
) CLUSTERED INTO 12 SHARDS PARTITIONED BY (month);
