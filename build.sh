#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala las dependencias
pip install -r requirements.txt

# Recolecta los archivos estáticos
python manage.py collectstatic --no-input

# Corre las migraciones
python manage.py migrate