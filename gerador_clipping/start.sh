#!/bin/bash
# Migrate the database first
echo "Migrating the database before starting the server"
python manage.py makemigrations
python manage.py migrate