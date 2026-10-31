## Running the app with Neon and Docker Compose

1. Copy environment file:

   ```bash
   cp .env.example .env
   ```

   Set `JWT_SECRET` to a long random value. Neon fills in the database and Auth
   URLs in the next step.

2. Link this checkout to the Neon project and deploy its declared Postgres and
   Auth services:

   ```bash
   npx neon@latest init -y --org-id org-raspy-firefly-85439177 \
     --project-id morning-paper-37929930 --branch production \
     --services postgres,auth
   npx neon@latest deploy
   ```

   The deploy command writes `DATABASE_URL`, `DATABASE_URL_UNPOOLED`,
   `NEON_AUTH_BASE_URL`, and `NEON_AUTH_JWKS_URL` to `.env`.

3. Build and start the API container:

   ```bash
   docker compose up --build -d
   ```

4. Apply migrations using Neon’s direct (unpooled) URL:

   ```bash
   docker compose exec web sh -c \
     'DATABASE_URL="$DATABASE_URL_UNPOOLED" flask --app '\''backend_project:create_app("production")'\'' db upgrade'
   ```

5. Verify the health endpoint:

   ```bash
   curl -i http://localhost:8000/health
   ```

   Expected result: `HTTP/1.1 200 OK` and `{"status":"ok"}`.

6. Restart the API container:

   ```bash
   docker compose restart web
   ```

   Neon stores database data remotely; it is not tied to the container lifecycle.