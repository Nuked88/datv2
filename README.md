# This is my first repo's readme file
#postgres installation
/usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/postgresql/10/main -l logfile restart

psql
CREATE ROLE <username> SUPERUSER LOGIN REPLICATION CREATEDB CREATEROLE;
CREATE DATABASE <username> OWNER <username>;
\q