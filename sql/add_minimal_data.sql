
USE `provenance`;

-- Insert a mythical service for testing (unit, integration, functional)
INSERT INTO Service (service_name, service_desc, service_link,
    service_ipaddress, service_group, service_type, service_version)
    VALUES ('Kahn - Data Commons', 'A test applicaion',
        'http://data.iplantcollaborative.org/test', '127.0.0.1',
        'Data Commons - TEST', 'TEST', 0.0);
INSERT INTO Service (service_name, service_desc, service_link,
    service_ipaddress, service_group, service_type, service_version)
    VALUES ('Kahn - Data Commons', 'A test applicaion - DEV',
        'http://data.iplantcollaborative.org/test', '127.0.0.1',
        'Data Commons', 'DEV', 0.1);

-- Insert categories associated with our mythical services
INSERT INTO Category (category_name, category_desc)
    VALUES ('dc-view', 'A read-only operation within Data Commons');
INSERT INTO Category (category_name, category_desc)
    VALUES ('dc-action', 'An action that mutates state within Data Commons');
INSERT INTO Category (category_name, category_desc)
    VALUES ('dc-admin', 'Operations carried out by admin user within Data Commons');

-- Insert events associated with the categories & mythical services
INSERT INTO Event (event_name, event_desc)
    VALUES ('root-list', 'Listing of root folder');
INSERT INTO Event (event_name, event_desc)
    VALUES ('home', 'Get path to user\'s home directory');
INSERT INTO Event (event_name, event_desc)
    VALUES ('download', 'Download a file');
INSERT INTO Event (event_name, event_desc)
    VALUES ('create-file', 'Create a file');
INSERT INTO Event (event_name, event_desc)
    VALUES ('edit-file', 'Edit or modification for a file');
INSERT INTO Event (event_name, event_desc)
    VALUES ('delete-file', 'Delete a file');
INSERT INTO Event (event_name, event_desc)
    VALUES ('create-folder', 'Create a folder');
INSERT INTO Event (event_name, event_desc)
    VALUES ('edit-folder', 'Edit or modification for a folder');
INSERT INTO Event (event_name, event_desc)
    VALUES ('delete-folder', 'Delete a folder');