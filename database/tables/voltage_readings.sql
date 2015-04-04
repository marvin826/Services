


CREATE TABLE voltage_readings (
	sec_since_epoch integer,
	sensor_id integer,
	voltage real,
	PRIMARY KEY(sec_since_epoch, sensor_id))

