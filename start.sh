#!/bin/sh

python app/init_db.py
python app/seed_db.py

exec python run.py