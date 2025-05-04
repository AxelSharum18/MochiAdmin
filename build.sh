#!/usr/bin/env bash

set -o errexit
# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py collectstatic --noinput
python manage.py migrate