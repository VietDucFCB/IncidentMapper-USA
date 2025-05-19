#!/bin/bash
set -e

echo "Initializing Superset..."

# Create an admin user
superset fab create-admin \
    --username admin \
    --firstname Superset \
    --lastname Admin \
    --email admin@superset.com \
    --password admin

# Initialize the database
superset db upgrade

# Create default roles and permissions
superset init

# Load example data (optional - remove if not needed)
# superset load-examples

# Setup your PostgreSQL database connection
superset set-database-uri \
    --database-name "superset" \
    --uri "postgresql://superset:superset@db:5432/superset"

echo "Superset initialization completed!"