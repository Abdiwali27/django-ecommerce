#!/usr/bin/env bash

set -o errexit

echo "======================================"
echo "Installing dependencies..."
echo "======================================"

python -m pip install -r requirements.txt

echo "======================================"
echo "Running migrations..."
echo "======================================"

python manage.py migrate --noinput

echo "======================================"
echo "Collecting static files..."
echo "======================================"

python manage.py collectstatic --noinput

echo "======================================"
echo "Build completed successfully."
echo "======================================"