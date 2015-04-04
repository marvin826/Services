
CREATE TABLE door_readings (
	sec_since_epoch integer,
	sensor_id integer,
	door_state integer,
	door_id integer,
	PRIMARY KEY(sec_since_epoch, sensor_id))
