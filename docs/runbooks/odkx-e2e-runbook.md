# Smart Field — ODK‑X End‑to‑End Architecture Runbook (v2)

> **Scope:** Django SmartFieldDashboard ↔ PG15 Analytics (FDW→ODK‑X) ↔ ODK‑X Endpoint stack; Nginx/Gunicorn; GitOps.
>
> **This version adds:** clear .env layout, Dockerized PG15 port mapping, read‑only DB role procedure, service checks,
> safe rebase/merge steps, and a practical troubleshooting appendix based on the issues we solved today.

---

## 0) High‑level architecture

- **Django App:** `SmartFieldDashboard` (Gunicorn on `127.0.0.1:8010`, proxied by Nginx as `https://smartfield.reslab.dev/`).
- **Static/Media:** served by Nginx from `/var/www/sfdash/{static,media}`. Django `STATIC_URL='/static/'`, `MEDIA_URL='/media/'`.
- **ODK‑X data access:** via **PG15 analytics** container that exposes host **5433 → container 5432**.
  - We read from DB **`postgres`**, schema **`odkx`**.
  - **Read‑only role:** `smartfield_ro` (LOGIN) with `USAGE`+`SELECT` on schema/tables.
  - Django protects writes with `DATABASE_ROUTERS = ['smartfield_dashboard.routers.ODKXReadOnlyRouter']`.
- **ODK‑X Endpoint stack:** LDAP + Sync Endpoint + Web UI (separate containers, fronted by Nginx under `odkx.reslab.dev`).

```
Client ─HTTPS─> Nginx (smartfield.reslab.dev)
                  └─► Gunicorn :8010 ─► Django SmartFieldDashboard
                                     └─► psycopg2 ─► Host:5433 → [Docker PG15:5432] (DB: postgres, schema: odkx)
```

---

## 1) Prerequisites (one‑time)

- Ubuntu host with:
  - `docker` and (if used) `docker compose`/Swarm for ODK‑X stack.
  - `python3`, `venv`, and `postgresql-client` (for `psql` on the host).
- System user **`shaykins`**, virtualenv `~/venvs/sfdash`.
- Nginx vhost `smartfield.reslab.dev` proxying all paths to `http://127.0.0.1:8010`.
- **Git (SSH):**
  ```bash
  ssh -T git@github.com              # must succeed
  git remote set-url origin git@github.com:henrymwaka/SmartFieldDashboard.git
  ```

---

## 2) Environment configuration (`.env`)

> Location: `/home/shaykins/Projects/SmartFieldDashboard/.env` (permissions `600`). **Never commit secrets.**

Minimal working set (redact secrets):

```dotenv
# Django SMTP (example; use App Password for Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=smartfield3@gmail.com
EMAIL_HOST_PASSWORD=********
DEFAULT_FROM_EMAIL=SmartField <smartfield3@gmail.com>

# Core
SECRET_KEY=********
ALLOWED_HOSTS=smartfield.reslab.dev,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://smartfield.reslab.dev http://smartfield.reslab.dev

# --- ODKX external DB ---  (PG15 analytics container exposes host 5433 → container 5432)
ODKX_DB_HOST=127.0.0.1
ODKX_DB_PORT=5433
ODKX_DB_NAME=postgres        # <‑ schema 'odkx' lives here
ODKX_DB_USER=smartfield_ro
ODKX_DB_PASSWORD=********     # set this explicitly (see §3)
ODKX_DB_SSLMODE=prefer
ODKX_ENABLED=false            # documentation flag (not consumed by settings.py)
```

**Rules:**

- Ensure **only one** block for `ODKX_DB_*` (duplicates can mask the correct value).
- Keep `.env.example` non‑secret with placeholders.
- File permissions: `chmod 600 .env`.

---

## 3) PG15 analytics (Docker) — read‑only role setup

### 3.1 Find the container that exposes 5433

```bash
docker ps --format 'table {{.ID}}\t{{.Names}}\t{{.Ports}}' | awk '/0\.0\.0\.0:5433->5432/'
# Expected: a row like: pg15_analytics  0.0.0.0:5433->5432/tcp
```

Optionally confirm from the host:

```bash
ss -lntp | grep ':5433 '        # shows docker-proxy listening on 0.0.0.0:5433
```

### 3.2 Enter psql as superuser and set the password

```bash
CID="$(docker ps --format '{{.ID}}\t{{.Ports}}' | awk '/0\.0\.0\.0:5433->5432/ {print $1; exit}')"
docker exec -it -u postgres "$CID" psql -U postgres -d postgres
```

**Inside psql:**

```sql
\du smartfield_ro                 -- role should exist and be LOGIN (Attributes shows '…')
\password smartfield_ro           -- type the password twice (matches .env ODKX_DB_PASSWORD)
-- Make sure it's a login role (idempotent):
ALTER ROLE smartfield_ro LOGIN;

-- Grant read-only access to schema 'odkx' in DB 'postgres':
GRANT CONNECT ON DATABASE postgres TO smartfield_ro;
GRANT USAGE ON SCHEMA odkx TO smartfield_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA odkx TO smartfield_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA odkx GRANT SELECT ON TABLES TO smartfield_ro;

-- Optional hardening (prevent writes/creates):
REVOKE CREATE ON SCHEMA odkx FROM PUBLIC, smartfield_ro;
```

> **Note:** The database is **`postgres`**; the data lives under schema **`odkx`**. This is why `inet_server_port()` returns **5432** when queried from inside the container—it’s the container’s port; the host maps **5433→5432**.

### 3.3 Test from host and from Django

**Host psql:**

```bash
PW="$(awk -F= '/^ODKX_DB_PASSWORD=/{print substr($0,index($0,"=")+1)}' .env | tr -d '\r')"
PGPASSWORD="$PW" psql -h 127.0.0.1 -p 5433 -U smartfield_ro -d postgres   -c "select current_user, current_database(), inet_server_port();"
# Expect: smartfield_ro | postgres | 5432
```

**Django (without using manage.py shell):**

```bash
source ~/venvs/sfdash/bin/activate
python - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smartfield_dashboard.settings')
django.setup()
from django.db import connections
with connections['odkx'].cursor() as c:
    c.execute("select current_user, current_database(), inet_server_port()")
    print("Django DB OK:", c.fetchone())
PY
# Expect: ('smartfield_ro', 'postgres', 5432)
```

---

## 4) Django application settings (sanity)

`smartfield_dashboard/settings.py` key points:

- **Routers:**  
  `DATABASE_ROUTERS = ['smartfield_dashboard.routers.ODKXReadOnlyRouter']`
- **App mount:** `FORCE_SCRIPT_NAME = None` (app lives at site root; Nginx proxies `/`).
- **Static/Media paths:**
  ```python
  STATIC_URL = '/static/'
  STATIC_ROOT = r'/var/www/sfdash/static'
  MEDIA_URL = '/media/'
  MEDIA_ROOT = r'/var/www/sfdash/media'
  ```
- **Default DB:** SQLite at `BASE_DIR/db.sqlite3`.
- **ODKX connection:** `DATABASES['odkx']` pulls its creds from `.env` via `decouple`.

Sanity check:

```bash
source ~/venvs/sfdash/bin/activate
python - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smartfield_dashboard.settings')
django.setup()
from django.conf import settings
print("FORCE_SCRIPT_NAME:", settings.FORCE_SCRIPT_NAME)
print("ODKX:", settings.DATABASES['odkx']['HOST'], settings.DATABASES['odkx']['PORT'], settings.DATABASES['odkx']['USER'])
PY
```

---

## 5) Gunicorn service + Nginx

### 5.1 Service control

```bash
sudo systemctl restart gunicorn-sfdash
sudo systemctl status gunicorn-sfdash --no-pager -l | sed -n '1,40p'
sudo journalctl -u gunicorn-sfdash -n 50 --no-pager
```

**Expected local health checks:**

```bash
# Gunicorn direct
curl -I http://127.0.0.1:8010/              # 302 to /login/?next=/
curl -I http://127.0.0.1:8010/admin/        # 302 to /admin/login/?next=/admin/
curl -I http://127.0.0.1:8010/api/          # 404 is fine if no API root view

# Through Nginx
curl -I https://smartfield.reslab.dev/admin/ | grep -i '^HTTP\|^Location:'
```

### 5.2 Nginx snippets (reference)

```
server_name smartfield.reslab.dev;
location / {
    proxy_pass http://127.0.0.1:8010;
    # ... usual proxy headers/timeouts ...
}
```

---

## 6) GitOps: safe update flow

```bash
# Sanity before changes
git status -s

# Commit the real fix (e.g., routers.py + settings.py)
git add smartfield_dashboard/routers.py smartfield_dashboard/settings.py
git commit -m "Fix router import + readonly routing"

# Tag a working build
git tag -a prod-YYYY-MM-DD -m "Site stable after router fix"
git push origin main --tags

# If remote ahead: rebase cleanly
git fetch origin
git pull --rebase origin main
# Resolve conflicts carefully; preserve DATABASE_ROUTERS line
git add <fixed files>
git rebase --continue
git push origin main --tags
```

**Merge conflict tip:** If `settings.py` conflicts, keep your `DATABASE_ROUTERS` and `FORCE_SCRIPT_NAME=None` lines. Avoid duplicate `ODKX_DB_*` entries.

---

## 7) Common pitfalls & fixes

- **`decouple.UndefinedValueError: ODKX_DB_PASSWORD not found`**  
  → Add it to `.env`, restart Gunicorn.

- **`Permission denied (publickey)` pushing to GitHub**  
  → Use SSH remote: `git@github.com:henrymwaka/SmartFieldDashboard.git`, ensure your public key is added to GitHub and ssh-agent loaded.

- **`ModuleNotFoundError: smartfield_dashboard.routers`**  
  → Ensure `smartfield_dashboard/routers.py` exists and is committed; restart.

- **404 on `/api/`**  
  → Expected if no DRF API root view is defined; Admin and pages should still 302/200.

- **Mismatch ports in diagnostics (`inet_server_port() = 5432` vs host 5433)**  
  → Normal: container listens on 5432; host maps 5433→5432.

- **Multiple `ODKX_DB_PASSWORD` lines in `.env`**  
  → Delete duplicates; keep exactly one. Confirm with `grep -n '^ODKX_DB_PASSWORD=' .env`.

---

## 8) Backup & rollback

- **Backup code & DB (SQLite default):**
  ```bash
  tar czf ~/sfdash-$(date +%F)-repo.tgz --exclude='env' --exclude='staticfiles' .
  cp db.sqlite3 ~/sfdash-$(date +%F)-db.sqlite3
  ```
- **Rollback to a tag:**
  ```bash
  git fetch --tags
  git checkout tags/prod-YYYY-MM-DD -b hotfix-rollback
  # verify, then deploy (or reset main to that tag if desired)
  ```

---

## 9) Operational checklist (TL;DR)

1. **.env** contains one ODKX block; `DB_NAME=postgres`, `USER=smartfield_ro`, `PASSWORD=…`, `PORT=5433`.
2. **PG15** container exposes `0.0.0.0:5433->5432`; role `smartfield_ro` has `USAGE/SELECT` on schema `odkx`.
3. **Host psql test** succeeds.
4. **Django test** (`Django DB OK: ('smartfield_ro','postgres',5432)`) succeeds.
5. **Gunicorn** running & Nginx proxying `/` (login redirects and admin are 302).
6. **Routers** file exists; **FORCE_SCRIPT_NAME=None**.

---

## 10) Appendix — Commands you’ll reuse

```bash
# Detect container for 5433
docker ps --format '{{.ID}}\t{{.Names}}\t{{.Ports}}' | awk '/0\.0\.0\.0:5433->5432/'

# Enter psql as postgres in that container
CID="$(docker ps --format '{{.ID}}\t{{.Ports}}' | awk '/0\.0\.0\.0:5433->5432/ {print $1; exit}')"
docker exec -it -u postgres "$CID" psql -U postgres -d postgres

# Host psql quick test
PW="$(awk -F= '/^ODKX_DB_PASSWORD=/{print substr($0,index($0,"=")+1)}' .env | tr -d '\r')"
PGPASSWORD="$PW" psql -h 127.0.0.1 -p 5433 -U smartfield_ro -d postgres -c 'select 1;'

# Django URL map (requires django-extensions)
python manage.py show_urls | head -n 20
```

---

## 11) What changed today (for posterity)

- Resolved Git push/auth by switching to SSH and fixing rebase conflicts.
- Restored `smartfield_dashboard/routers.py` and confirmed `DATABASE_ROUTERS` in settings.
- Standardized `.env` (deduplicated ODKX entries; set correct port and DB name).
- Discovered analytics DB is `postgres` with schema `odkx` (not a DB named `odkx`).
- Set/reset `smartfield_ro` password via `\password` and verified from host and Django.
- Confirmed Nginx→Gunicorn path works; kept `FORCE_SCRIPT_NAME=None` (app at site root).
