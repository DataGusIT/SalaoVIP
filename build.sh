#!/usr/bin/env bash
# Sair se der erro
set -o errexit

# 1. Instalar dependências
pip install -r requirements.txt

# 2. Coletar arquivos estáticos (CSS/JS) para o Whitenoise servir
python manage.py collectstatic --no-input

# 3. Aplicar migrações no banco de dados (Supabase)
python manage.py migrate