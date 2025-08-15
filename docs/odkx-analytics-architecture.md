# ODK‑X → Postgres 15 Analytics via FDW — Architecture & Runbook

**Owner:** SmartFieldDashboard

---

## 1) Overview (What & Why)
Your Django 5.2 app must use a modern Postgres (≥14), while ODK‑X runs on Postgres 9.6. We introduce a **Postgres 15 “analytics”** instance that connects to 9.6 with **postgres_fdw** (Foreign Data Wrapper). Django only talks to PG15; PG15 proxies reads to ODK‑X and can cache data in **Materialized Views (MVs)**.

```
Django (5.2)  ──>  Postgres 15 (analytics)  ──[FDW]──>  ODK‑X Postgres 9.6
     read‑only          supported & local                  legacy, unchanged
```

### Benefits
- **Compatibility:** Django stays supported while ODK‑X remains untouched.
- **Safety:** Read‑only at Django and DB layers; migrations never hit ODK‑X.
- **Performance:** Optional MVs decouple reads from ODK‑X and speed up queries.
- **Operability:** Clear secrets handling, scheduled refresh, simple verification.

---

## 2) Environment quick facts (current setup)
- **Django project root:** `~/Projects/SmartFieldDashboard`
- **.env keys:** `ODKX_DB_NAME=postgres`, `ODKX_DB_USER=smartfield_ro`, `ODKX_DB_PASSWORD=…`, `ODKX_DB_HOST=127.0.0.1`, `ODKX_DB_PORT=5433`
- **PG15 container (analytics):** `pg15_analytics` (host‑mapped to `127.0.0.1:5433`)
- **ODK‑X 9.6 container:** e.g. `d76008c45650` (port 5432 inside Docker/Swarm)
- **FDW remote server:** `odkx9` → points to `host.docker.internal:5432` DB `postgres`
- **Schemas:**
  - On 9.6: `odk_sync`
  - On PG15 (foreign tables): `odkx` (imported via FDW from `odk_sync`)
  - On PG15 (materialized views): `analytics`
- **App role on PG15:** `smartfield_ro` (read‑only)
- **FDW user on 9.6:** `odkx_readonly` (read‑only)

> **Tip:** Use a password manager; avoid putting secrets directly in scripts or crontab. Prefer `.env` for Django and `~/.pgpass` for cron/psql.

---

## 3) Django configuration
### settings.py (key parts)
- Second DB connection named `odkx` points to **PG15** (not 9.6):
- Keep connection warm and enable health checks.
- Set a convenient `search_path` so unqualified lowercase names resolve to `odkx`.
- Block writes/migrations to `odkx` via a router.

**Example:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'odkx': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('ODKX_DB_NAME', default='postgres'),
        'USER': config('ODKX_DB_USER', default='smartfield_ro'),
        'PASSWORD': config('ODKX_DB_PASSWORD'),
        'HOST': config('ODKX_DB_HOST', default='127.0.0.1'),
        'PORT': config('ODKX_DB_PORT', cast=int, default=5433),
        'CONN_MAX_AGE': 300,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'options': '-c search_path=odkx,analytics,public',
        },
    },
}

DATABASE_ROUTERS = ['smartfield_dashboard.routers.ODKXReadOnlyRouter']
```

**DB Router (read‑only on `odkx`):**
```python
# smartfield_dashboard/routers.py
class ODKXReadOnlyRouter:
    def db_for_write(self, model, **hints):
        return 'default'
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db != 'odkx'
```

---

## 4) Postgres 9.6 (ODK‑X) grants
Run inside the 9.6 container as `postgres`:
```sql
GRANT USAGE ON SCHEMA odk_sync TO odkx_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA odk_sync TO odkx_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA odk_sync GRANT SELECT ON TABLES TO odkx_readonly;
```

---

## 5) Postgres 15 (analytics) — FDW bridge
From PG15 as `postgres`:
```sql
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SERVER IF NOT EXISTS odkx9
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'host.docker.internal', port '5432', dbname 'postgres');

-- Local schema to host foreign tables
CREATE SCHEMA IF NOT EXISTS odkx;

-- Import remote schema
IMPORT FOREIGN SCHEMA odk_sync FROM SERVER odkx9 INTO odkx;

-- App role
CREATE ROLE smartfield_ro LOGIN PASSWORD 'DJANGO_RO_PASSWORD';
GRANT USAGE ON SCHEMA odkx TO smartfield_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA odkx TO smartfield_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA odkx GRANT SELECT ON TABLES TO smartfield_ro;

-- FDW user mapping (PG15 role → 9.6 credentials)
CREATE USER MAPPING IF NOT EXISTS FOR smartfield_ro SERVER odkx9
  OPTIONS (user 'odkx_readonly', password 'ODKX9_PASSWORD');
-- (Optional) mapping for postgres if you refresh as postgres too
CREATE USER MAPPING IF NOT EXISTS FOR postgres SERVER odkx9
  OPTIONS (user 'odkx_readonly', password 'ODKX9_PASSWORD');
```

**Connectivity checks:**
```sql
SELECT current_database(), current_user, now();
SELECT COUNT(*) FROM odkx._backend_actions;  -- lowercase, no quotes
SELECT COUNT(*) FROM odkx."__ODKTABLES__TABLE_ENTRY4";  -- uppercase requires quotes
```

---

## 6) Ergonomic **shim views** (no refresh needed)
Create friendly lowercase views for uppercase ODK‑X tables in `odkx`:
```sql
CREATE OR REPLACE VIEW odkx.table_entry4 AS
  SELECT * FROM odkx."__ODKTABLES__TABLE_ENTRY4";
GRANT SELECT ON odkx.table_entry4 TO smartfield_ro;

CREATE OR REPLACE VIEW odkx.table_file_info4 AS
  SELECT * FROM odkx."__ODKTABLES__TABLE_FILE_INFO4";
GRANT SELECT ON odkx.table_file_info4 TO smartfield_ro;

CREATE OR REPLACE VIEW odkx.manifest_etags AS
  SELECT * FROM odkx."__ODKTABLES__MANIFEST_ETAGS";
GRANT SELECT ON odkx.manifest_etags TO smartfield_ro;

CREATE OR REPLACE VIEW odkx.interaction_log AS
  SELECT * FROM odkx."__ODKTABLES__INTERACTION_LOG";
GRANT SELECT ON odkx.interaction_log TO smartfield_ro;
```

Now you can query without quotes:
```sql
SELECT COUNT(*) FROM odkx.table_entry4;
SELECT * FROM odkx.table_file_info4 LIMIT 10;
```

---

## 7) Materialized Views (MVs) in `analytics`
**Purpose:** snapshot FDW tables and/or aggregations for faster, decoupled reads.

**Pattern:**
```sql
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.backend_actions_mv AS
  SELECT * FROM odkx._backend_actions WITH NO DATA;
ALTER MATERIALIZED VIEW analytics.backend_actions_mv OWNER TO smartfield_ro;
GRANT SELECT ON analytics.backend_actions_mv TO smartfield_ro;

-- Refresh when you choose
REFRESH MATERIALIZED VIEW analytics.backend_actions_mv;
```

**MVs you created (examples):**
- `analytics.backend_actions_mv`
- `analytics.tablefiles_ref_mv`
- `analytics.server_prefs_mv`
- `analytics.task_lock_mv`
- `analytics.table_entry4_mv`
- `analytics.table_file_info4_mv`
- `analytics.manifest_etags_mv`
- `analytics.interaction_log_mv`

> **Concurrent refresh (optional):** Add a **unique index** on the MV’s natural key, then use `REFRESH MATERIALIZED VIEW CONCURRENTLY ...` to avoid blocking readers.

---

## 8) Secrets & scheduling
### Password rotation
- Rotate PG15 role password:
  ```sql
  ALTER ROLE smartfield_ro WITH PASSWORD 'DJANGO_RO_PASSWORD';
  ```
  Update Django `.env`: `ODKX_DB_PASSWORD=DJANGO_RO_PASSWORD`.
- Rotate 9.6 FDW user password:
  ```sql
  -- on 9.6
  ALTER USER odkx_readonly WITH PASSWORD 'ODKX9_PASSWORD';
  -- update PG15 mappings
  ALTER USER MAPPING FOR smartfield_ro SERVER odkx9 OPTIONS (SET password 'ODKX9_PASSWORD');
  ALTER USER MAPPING FOR postgres      SERVER odkx9 OPTIONS (SET password 'ODKX9_PASSWORD');
  ```

### Cron refresh without plain passwords
Use `~/.pgpass` (mode 600):
```
127.0.0.1:5433:postgres:smartfield_ro:DJANGO_RO_PASSWORD
```
**Crontab** (example: nightly 01:10):
```
10 1 * * * /usr/bin/psql -h 127.0.0.1 -p 5433 -U smartfield_ro -d postgres \
  -c "REFRESH MATERIALIZED VIEW analytics.backend_actions_mv" \
  >/tmp/odkx_mv_refresh.log 2>&1
```

**Refresh all MVs** in schema via DO block (wrap in a script/cron if desired):
```sql
DO $$ DECLARE r RECORD; BEGIN
  FOR r IN SELECT schemaname, matviewname FROM pg_matviews WHERE schemaname='analytics' LOOP
    EXECUTE format('REFRESH MATERIALIZED VIEW %I.%I', r.schemaname, r.matviewname);
  END LOOP;
END $$;
```

**(Optional) Django management command** `dashboard/management/commands/refresh_odkx.py` to refresh one/all MVs programmatically.

---

## 9) Verification & troubleshooting
### Quick tests
- From Django:
  ```python
  from django.db import connections
  with connections['odkx'].cursor() as cur:
      cur.execute("SELECT current_database(), current_user")
      print(cur.fetchone())
      cur.execute("SELECT COUNT(*) FROM _backend_actions")
      print(cur.fetchone())
  ```
- From PG15 as app role:
  ```bash
  PGPASSWORD=DJANGO_RO_PASSWORD psql -h 127.0.0.1 -p 5433 -U smartfield_ro -d postgres -c "SELECT COUNT(*) FROM odkx._backend_actions"
  ```

### Common errors → fixes
- **`password authentication failed for user "odkx_readonly"`**
  - The FDW mapping password on PG15 doesn’t match 9.6. Run `ALTER USER MAPPING ... OPTIONS (SET password ...)`.
- **`PostgreSQL 14 or later is required (found 9.6)`**
  - Django accidentally points at 9.6. Ensure `.env` + `settings.py` point to PG15 (`127.0.0.1:5433`, user `smartfield_ro`).
- **`permission denied for foreign table ...`**
  - Re‑grant on PG15: `GRANT USAGE ON SCHEMA odkx; GRANT SELECT ON ALL TABLES IN SCHEMA odkx TO smartfield_ro;`.
- **Uppercase table errors**
  - Use quotes or shim views: `"__ODKTABLES__TABLE_ENTRY4"` or `odkx.table_entry4`.
- **MV refresh fails**
  - Owner must refresh; set `OWNER TO smartfield_ro`. Ensure FDW mapping exists for that role.

---

## 10) Operational runbook (copy‑paste friendly)
### Verify end‑to‑end
```bash
# Django → PG15 user
python manage.py shell -c "from django.db import connections as c; cur=c['odkx'].cursor(); cur.execute('select current_user, current_database()'); print(cur.fetchone())"

# PG15 → ODK‑X via FDW
PGPASSWORD=DJANGO_RO_PASSWORD psql -h 127.0.0.1 -p 5433 -U smartfield_ro -d postgres -c "select count(*) from odkx._backend_actions"
```

### Rotate secrets
```sql
-- PG15 (analytics)
ALTER ROLE smartfield_ro WITH PASSWORD 'DJANGO_RO_PASSWORD';
-- Update Django .env accordingly

-- 9.6 (ODK‑X)
ALTER USER odkx_readonly WITH PASSWORD 'ODKX9_PASSWORD';
-- PG15: update FDW mappings
ALTER USER MAPPING FOR smartfield_ro SERVER odkx9 OPTIONS (SET password 'ODKX9_PASSWORD');
ALTER USER MAPPING FOR postgres      SERVER odkx9 OPTIONS (SET password 'ODKX9_PASSWORD');
```

### Create a new MV (template)
```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.<name>_mv AS
  SELECT ... FROM odkx.<table_or_view> WITH NO DATA;
ALTER MATERIALIZED VIEW analytics.<name>_mv OWNER TO smartfield_ro;
GRANT SELECT ON analytics.<name>_mv TO smartfield_ro;
-- then
REFRESH MATERIALIZED VIEW analytics.<name>_mv;
```

### Refresh all analytics MVs (SQL block)
```sql
DO $$ DECLARE r RECORD; BEGIN
  FOR r IN SELECT schemaname, matviewname FROM pg_matviews WHERE schemaname='analytics' LOOP
    EXECUTE format('REFRESH MATERIALIZED VIEW %I.%I', r.schemaname, r.matviewname);
  END LOOP;
END $$;
```

---

## 11) Glossary
- **FDW (Foreign Data Wrapper):** lets PG15 access tables in PG9.6 as if local.
- **Foreign table:** a local pointer to a remote table (live, no data stored).
- **Materialized View:** physical snapshot of a query result, refreshed on demand.
- **Shim view:** simple non‑materialized view to provide clean names or mild transforms.
- **search_path:** schema order Postgres searches when resolving unqualified names.

---

## 12) Notes & future enhancements
- Add business‑level MVs (aggregations, filters) with appropriate indexes.
- If refresh time matters, consider **CONCURRENTLY** with a unique index.
- Consider monitoring (refresh time, row counts) and alerting if they drift.
- Keep `.env` and `~/.pgpass` **out of version control**; restrict permissions.

---

*Document version: v1.0 — generated for the SmartFieldDashboard ODK‑X integration.*

