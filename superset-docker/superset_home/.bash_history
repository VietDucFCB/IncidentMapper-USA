superset db upgrade
superset fab create-admin     --username admin     --firstname Admin     --lastname Admin     --email admin@superset.com     --password admin123
superset init
exit
superset set-database-uri     --database-name "PostgreSQL"     --uri "postgresql://superset:superset@db:5432/superset"
exit
apt-get update && apt-get install -y postgresql-client
psql -h db -U superset -d superset
exit
apt-get update
exit
superset db check
su postgres
superset db list
exit
