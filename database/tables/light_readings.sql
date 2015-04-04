


CREATE TABLE light_readings (
	sec_since_epoch integer,
	sensor_id integer,
	light real,
	PRIMARY KEY(sec_since_epoch, sensor_id))

