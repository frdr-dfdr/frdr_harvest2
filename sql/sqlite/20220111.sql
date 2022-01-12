CREATE TABLE IF NOT EXISTS geonames (
geonames_id INTEGER PRIMARY KEY NOT NULL,
country text,
province_state text,
city text,
northLat NUMERIC,
southLat NUMERIC,
eastLon NUMERIC,
westLon NUMERIC,
last_modified_timestamp int DEFAULT 0);

ALTER TABLE geoplace
ADD COLUMN record_uuid TEXT
CONSTRAINT fk_uuid REFERENCES records(record_uuid)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE geoplace
ADD COLUMN geonames_id INTEGER
CONSTRAINT fk_geonames REFERENCES geonames(geonames_id)
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE geoplace
ADD COLUMN upstream_modified_timestamp INTEGER DEFAULT 0;

ALTER TABLE geoplace
ADD COLUMN geonames_associated_timestamp INTEGER DEFAULT 0;

ALTER TABLE geoplace
ADD COLUMN geodisy_review_status INTEGER DEFAULT 0;

UPDATE geoplace set record_uuid = (select record_uuid from records_x_geoplace where records_x_geoplace.geoplace_id = geoplace.geoplace_id);

DROP TABLE records_x_geoplace;

ALTER TABLE geobbox
ADD COLUMN geofile_id INTEGER
CONSTRAINT fk_geofile REFERENCES geofile(geofile_id)
ON UPDATE CASCADE ON DELETE CASCADE;
