#!/bin/bash
set -e

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    until pg_isready --host db --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"; do
        echo "waiting for the master database"
        sleep 2
    done
    mkdir -p "$PGDATA"
    rm -rf "${PGDATA:?}"/*
    PGPASSWORD="$REPLICATION_PASSWORD" pg_basebackup --host db --username replicator --pgdata "$PGDATA" --wal-method stream --write-recovery-conf --progress
    chown -R postgres:postgres /var/lib/postgresql
    chmod 0700 "$PGDATA"
fi

exec docker-entrypoint.sh postgres
