
CREATE TABLE temperature_readings (
	sec_since_epoch integer,
	sensor_id integer,
	temperature real),
	PRIMARY_KEY(sec_since_epoch, sensor_id)