#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# --- LINHA NOVA: Roda nosso script de criar admin ---
python manage.py createsuperuser_auto