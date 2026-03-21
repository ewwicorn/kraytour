# Kraytour Backend

FastAPI + PostgreSQL + MinIO backend for the Kraytour tourism platform.

## Quick start

```bash
# 1. Copy env and fill in SECRET_KEY
cp .env.example .env   # or edit .env directly

# 2. Start infrastructure + app
docker compose up -d

# 3. Run migrations
docker compose exec backend alembic upgrade head

# 4. Seed demo data (tags + 5 locations)
docker compose exec backend python -m app.seed

# 5. Open API docs
open http://localhost:8000/docs
```

## Run tests

```bash
chmod +x test_api.sh
./test_api.sh                      # default: localhost:8000
./test_api.sh http://host:8000     # custom host
```

The script tests every endpoint end-to-end:
registers buyer / seller / admin users, exercises all auth flows,
creates / updates / activates / deletes a location, uploads and
deletes a file. Exits 0 on all-pass, 1 on any failure.

---

## Bug fixes applied (v0.1.0 → v0.1.1)

### 1. `db/session.py` — missing rollback on exception
**Before:** `yield session` with no error handling. Any exception inside
a route left the transaction open, blocking the connection.  
**After:** `try / commit → except / rollback → finally / close` pattern.

### 2. `core/config.py` — deprecated `class Config`, missing `is_production`
**Before:** Used Pydantic v1-style `class Config: env_file = ".env"`.
`session.py` referenced `settings.is_production` which didn't exist,
causing an `AttributeError` at startup.  
**After:** Migrated to `model_config = SettingsConfigDict(...)`.
Added `is_production` property.

### 3. `core/dependencies.py` — UUID type mismatch in DB query
**Before:** `payload.get("sub")` returns a plain `str`. Comparing it
directly against `User.id` (a UUID column) caused the SQLAlchemy query
to silently find nothing on PostgreSQL, so every authenticated request
returned 401.  
**After:** Cast with `uuid.UUID(user_id_str)` before the `select`.

### 4 + 5. `api/v1/files.py` — file read twice, size always 0
**Before:** `validate_file()` called `await file.read()` then
`file.file.seek(0)` (sync seek on an async stream). The upload handler
then called `len(await file.read())` a second time on an exhausted
stream, always returning `0`.  
**After:** `validate_file()` returns the `bytes` it read. The caller
uses those bytes for both the upload and the size field. Stream is
read exactly once.

### 6. `api/v1/files.py` — path parameters don't allow slashes
**Before:** `/{object_name}` and `/url/{object_name}` reject any object
name containing `/` with a 404.  
**After:** `/{object_name:path}` passes slashes through correctly.

### 7. `services/minio_service.py` — sync SDK blocking the event loop
**Before:** All MinIO calls (`put_object`, `stat_object`,
`remove_object`, `presigned_get_object`) ran directly on the asyncio
event loop, blocking every other request for the duration of each S3
operation (often 100ms–2s).  
**After:** Every blocking call is wrapped in `asyncio.to_thread()`.
The public API is now fully async.

### 8. `services/location_service.py` — `db.delete()` not awaited
**Before:** `db.delete(location)` (without `await`) created a
coroutine object and immediately discarded it. The object was never
marked for deletion, so `DELETE /locations/:id` returned 204 but the
record stayed in the database.  
**After:** `await db.delete(location)`.

### 9. `alembic/versions/fc51680e510a` — broken migration drops server_default
**Before:** The migration added `created_at NOT NULL` with
`server_default=func.now()`, then immediately called
`op.alter_column('users', 'created_at', server_default=None)`.
After that migration, every `INSERT INTO users` without an explicit
`created_at` raised `NOT NULL constraint violation`.  
**After:** Removed the `alter_column` call. The `server_default` is
kept so the column self-populates on insert.

### 10. `docker-compose.yml` — backend starts before postgres is ready
**Before:** `depends_on: [postgres, minio]` without health conditions.
Docker started the backend immediately after creating the postgres
container, long before PostgreSQL accepted connections. The app
crashed on the first DB call.  
**After:** Both `depends_on` entries use `condition: service_healthy`.
Backend waits for the `pg_isready` healthcheck to pass.
