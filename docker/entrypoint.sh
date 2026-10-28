#!/bin/sh
set -e

# Fallback wait for the database (compose healthcheck is the primary guard)
python - <<'PY'
import os
import sys
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

for attempt in range(30):
    try:
        connection.ensure_connection()
        break
    except Exception as exc:  # noqa: BLE001
        print(f"Waiting for database ({attempt + 1}/30): {exc}", flush=True)
        time.sleep(2)
else:
    sys.exit("Database not reachable, aborting.")
PY

python manage.py migrate --noinput

# Seed demo data only on first boot: cargar_datos creates date-based records
# (turnos/recetas) that would duplicate on every restart.
if [ "${LOAD_SEED_DATA:-true}" = "true" ]; then
    if python manage.py shell --verbosity 0 -c "import sys; from catalogo.models import Anteojo; sys.exit(0 if Anteojo.objects.exists() else 1)"; then
        echo "Seed data already present, skipping cargar_datos."
    else
        python manage.py cargar_datos
    fi
fi

exec "$@"
