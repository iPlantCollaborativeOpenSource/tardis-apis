--
--
--


ALTER TABLE Object
    CHANGE COLUMN object_id id INT(11),
    CHANGE COLUMN service_object_id object_id VARCHAR(128),
    ADD service_id INT(11) after uuid
;

ALTER TABLE Object
    DROP PRIMARY KEY,
    ADD PRIMARY KEY (service_id, object_id)
;

ALTER TABLE Object
    ADD FOREIGN KEY (service_id) REFERENCES Service(service_id)
;