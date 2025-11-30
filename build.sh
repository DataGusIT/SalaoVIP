#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Cria o admin (se não existir)
python manage.py createsuperuser_auto

# Popula o banco com os 8 cabeleireiros e serviços (se não existirem)
python manage.py populate_salao