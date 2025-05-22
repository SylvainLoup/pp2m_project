#!/usr/bin/env bash

# Installe les dépendances
pip install -r requirements.txt

# Applique les migrations
python manage.py migrate

# Collecte les fichiers statiques
python manage.py collectstatic --noinput