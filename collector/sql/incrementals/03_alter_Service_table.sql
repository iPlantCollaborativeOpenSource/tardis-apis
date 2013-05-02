--
--
--

-- Warning - you have to have data in the column ``service_key`` or the RDBMS
-- will just kick out a "duplicate entry" error.

ALTER TABLE Service ADD CONSTRAINT cons_service_key UNIQUE (service_key);