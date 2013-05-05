

ALTER TABLE Object DROP INDEX `uuid_UNIQUE`;

ALTER TABLE Object DROP INDEX `PRIMARY`;

ALTER TABLE Object
    ADD PRIMARY KEY Object(uuid)
;

ALTER TABLE Object
    ADD UNIQUE (service_id, object_id),
    ADD FOREIGN KEY (service_id) REFERENCES Service(service_id)
;

ALTER TABLE Object
    ADD FOREIGN KEY (parent_uuid) REFERENCES Object(uuid)
;