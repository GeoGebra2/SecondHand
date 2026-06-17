#!/bin/sh
set -eo pipefail

# run-migrations.sh
# Runs migration SQL files in /migrations in deterministic order.
# Supports fresh-db (no notification table) and existing-db cases.

MYSQL_CMD="mysql -h mysql -u root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE}"

echo "Waiting for MySQL to be available..."
# simple wait loop
tries=0
until ${MYSQL_CMD} -e 'SELECT 1' >/dev/null 2>&1; do
  tries=$((tries+1))
  if [ $tries -gt 30 ]; then
    echo "MySQL did not become available in time" >&2
    exit 1
  fi
  sleep 2
done

echo "MySQL is reachable, starting migrations..."

# First, ensure base tables (create_notification_if_missing.sql) is always applied (it is idempotent)
if [ -f /migrations/000-create-notification-if-missing.sql ]; then
  echo "Applying 000-create-notification-if-missing.sql"
  ${MYSQL_CMD} < /migrations/000-create-notification-if-missing.sql
fi

# Then apply other migrations except the create-if-missing (order by name)
for f in $(ls /migrations/*.sql | grep -v '000-create-notification-if-missing.sql' | sort); do
  echo "Processing $f"
  case "$(basename $f)" in
    2026-06-17-fix-notification.sql)
      echo "Checking for existing legacy 'notification' table before running fix-notification..."
      has_old=$(${MYSQL_CMD} -sN -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='notification' AND table_type='BASE TABLE';")
      if [ "${has_old}" -eq 1 ]; then
        echo "Legacy notification table found — running migration $f"
        ${MYSQL_CMD} < "$f"
      else
        echo "No legacy notification table found — skipping $f"
      fi
      ;;
    *)
      echo "Applying $f"
      ${MYSQL_CMD} < "$f"
      ;;
  esac
done

echo "Migrations complete."