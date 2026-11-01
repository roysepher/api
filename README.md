# API

A Flask API with user registration and login, JWT authentication, and
user-owned notes. For local development it uses SQLite by default. Production
uses PostgreSQL and can validate tokens issued by Neon Auth.

## Run locally

Requirements: Python 3.12 or newer.

```bash
git clone https://github.com/roysepher/api.git
cd api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set a local JWT secret. The development configuration uses SQLite
(`instance/dev.db`) unless `DATABASE_URL` is set.

```bash
echo "JWT_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
```

Create or update the database tables, then start the Flask development server:

```bash
flask --app 'backend_project:create_app("development")' db upgrade
flask --app 'backend_project:create_app("development")' run --debug
```

The API is available at <http://127.0.0.1:5000>. Check that it is running:

```bash
curl -i http://127.0.0.1:5000/health
```

The health endpoint should return `200 OK` with `{"status":"ok"}`. To register
and log in locally, use a password between 12 and 128 characters:

```bash
curl -i http://127.0.0.1:5000/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"a-long-local-password"}'

curl -i http://127.0.0.1:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"a-long-local-password"}'
```

The login response contains an `access_token`. Send it as a bearer token to
protected endpoints, for example:

```bash
curl http://127.0.0.1:5000/notes \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

## Run with Docker Compose and Neon

Requirements: Docker with the Compose plugin, and a Neon project with Postgres
and Neon Auth enabled. The existing [`neon.ts`](./neon.ts) declares Neon Auth.

1. Copy the environment template and edit `.env`. Set `JWT_SECRET` to a
   randomly generated secret, and fill in the pooled and direct database
   connection strings plus the Neon Auth base URL and JWKS URL from your Neon
   project. Keep `.env` private; it is ignored by Git.

   ```bash
   cp .env.example .env
   ```

2. Build and start the API:

   ```bash
   docker compose up --build -d
   ```

3. Apply database migrations using the direct (unpooled) database connection:

   ```bash
   docker compose exec web sh -c \
     'DATABASE_URL="$DATABASE_URL_UNPOOLED" flask --app '\''backend_project:create_app("production")'\'' db upgrade'
   ```

4. Verify the service:

   ```bash
   curl -i http://localhost:8000/health
   ```

To view logs or stop the service:

```bash
docker compose logs -f web
docker compose down
```

## Deploy on Render

1. Push this repository to GitHub and create a **Web Service** in Render from
   the repository. Select the **Docker** runtime; Render will build the
   included `Dockerfile`.
2. Add these environment variables in the Render service settings:
   - `DATABASE_URL`: Neon pooled PostgreSQL connection string.
   - `DATABASE_URL_UNPOOLED`: Neon direct PostgreSQL connection string, used
     for migrations.
   - `JWT_SECRET`: a long, randomly generated secret.
   - `NEON_AUTH_BASE_URL` and `NEON_AUTH_JWKS_URL`: values from your Neon Auth
     project.
3. Configure the service's **Pre-Deploy Command** to apply migrations:

   ```sh
   DATABASE_URL="$DATABASE_URL_UNPOOLED" flask --app 'backend_project:create_app("production")' db upgrade
   ```

4. Set the health check path to `/health` and deploy. Render supplies `PORT`
   to the Docker container; do not set it yourself.

## API routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/register` | Register a username and password |
| `POST` | `/login` | Exchange credentials for a JWT |
| `GET` | `/whoami` | Get the authenticated user's ID and role |
| `GET` | `/me` | Get the authenticated user's ID |
| `GET`, `POST` | `/notes` | List or create the authenticated user's notes |
| `GET`, `PATCH`, `DELETE` | `/notes/<id>` | Read, update, or delete an owned note |
| `GET` | `/admin` | Admin-only example endpoint |

Protected routes require an `Authorization: Bearer <token>` header. Local
registration and login issue application JWTs. In production, the API can also
accept Neon Auth access tokens when the Neon Auth URLs are configured.
