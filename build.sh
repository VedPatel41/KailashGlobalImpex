#!/usr/bin/env bash
# Kailash Global Impex — Render Build Script
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Collecting static assets..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Seeding initial data (products & admin)..."
python manage.py seed_kgi_data

echo "==> Build completed successfully."
