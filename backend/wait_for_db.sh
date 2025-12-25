#!/bin/sh

echo "Waiting for postgres..."

while ! pg_isready -h minijira-postgres -U postgres > /dev/null 2>&1; do
    sleep 1
done

echo "Postgres is ready!"