#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala las dependencias
pip install -r requirements.txt

# Corre las migraciones
python manage.py migrate