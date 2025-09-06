# Weather Fortune — Monorepo 🌦️

AI-driven weather app that combines short-term forecasts (Open-Meteo) with climatological averages to provide long-range predictions. Frontend built with **Next.js**, backend with **FastAPI**, and a PostgreSQL database (Supabase in production).

---

## 🚀 Quickstart

1. Copy environment file:

   ```bash
   cp .env.example .env
   ```

   Adjust values (API keys, DB URL, etc).

2. Start services:

   ```bash
   docker compose up --build
   ```

3. Open apps:

   - **Web (Next.js):** [http://localhost:3000](http://localhost:3000)
   - **API (FastAPI):** [http://localhost:8000](http://localhost:8000)

---

## 📂 Project structure

```
Climate Data Exercise/
├─ docker-compose.yml
├─ .env.example
├─ .env
├─ apps/
│  ├─ web/                    # Next.js 15 + Tailwind + Framer Motion
│  │  ├─ app/
│  │  ├─ public/
│  │  ├─ Dockerfile
│  │  ├─ package.json
│  │  └─ next.config.ts
│  └─ api/                    # FastAPI (Python) + SQLAlchemy
│     ├─ alembic/             # Migration files and configuration
│     │  ├─ versions/         # Individual migration scripts
│     │  └─ env.py
│     ├─ app/                 # FastAPI application code
│     ├─ alembic.ini          # Alembic configuration
│     ├─ Dockerfile
│     └─ requirements.txt
├─ test_migration.py          # Database testing script
└─ README.md
```

---

## 🛠️ Services

- **Web**: Next.js 15, Tailwind CSS, Framer Motion
- **API**: FastAPI, SQLAlchemy, Alembic migrations
- **DB**: PostgreSQL (local via Docker, or Supabase in production)
- **Cache**: Redis (forecast caching, rate-limiting)

---

## 📑 Alembic workflow (migrations)

1. Generate a new migration file:

   ```bash
   docker compose run --rm api alembic revision -m "add new table"
   ```

2. Fill in the new file under `apps/api/alembic/versions/` with the actual schema changes (`upgrade()` and `downgrade()`).

3. Apply the migration:

   ```bash
   docker compose run --rm api alembic upgrade head
   ```

4. Verify in the database (Supabase UI or SQL query):

   ```sql
   SELECT * FROM alembic_version;
   SELECT table_name FROM information_schema.tables WHERE table_schema='public';
   ```

5. If you accidentally ran a migration with `pass`, roll it back, edit, and re-run:

   ```bash
   docker compose run --rm api alembic downgrade -1
   docker compose run --rm api alembic upgrade head
   ```

**Rule of thumb:** _Create → Fill → Run_. Never run `upgrade head` on a migration that still has `pass`.
