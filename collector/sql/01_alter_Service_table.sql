--
--
--

ALTER TABLE Service
    ADD service_key VARCHAR(10) NOT NULL after service_id
;

-- Now, add some data to that column so 3_alter_Service can add the constraint