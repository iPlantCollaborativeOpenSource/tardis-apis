
USE `mysql`;

-- development user, should only be used in local development
GRANT ALL PRIVILEGES ON *.* TO 'tardis'@'localhost'
    IDENTIFIED BY 'S0N1Cscr3wdr1V3r' WITH GRANT OPTION;
FLUSH PRIVILEGES;