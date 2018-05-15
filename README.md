# This is my first repo's readme file
# postgres installation
/usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/postgresql/10/main -l logfile restart

psql
CREATE ROLE <username> SUPERUSER LOGIN REPLICATION CREATEDB CREATEROLE;
CREATE DATABASE <username> OWNER <username>;
\q


CREATE TABLE words(
   ID INT PRIMARY KEY     NOT NULL,
   start           INT    NOT NULL DEFAULT 0,
   end            INT     NOT NULL DEFAULT 0,
   word        	TEXT
);

INSERT INTO films VALUES
    ('UA502', 'Bananas', 105, '1971-07-13', 'Comedy', '82 minutes');

UPDATE employees SET sales_count = sales_count + 1 WHERE id =
  (SELECT sales_person FROM accounts WHERE name = 'Acme Corporation');