## Running the app with Docker Compose

1. Copy environment file:

   ```bash
   cp .env.example .env
   ```

   Fill in the required values (for example `JWT_SECRET`, etc.).
   You do not need to set `DATABASE_URL` for Docker Compose; it is provided by `docker-compose.yml`.

2. Start the app and database:

   ```bash
   docker compose up --build
   ```

   This starts the `web` service (API) and the `db` service (PostgreSQL 16).

3. Run database migrations inside the web container:

   ```bash
   docker compose exec web flask --app 'backend_project:create_app("development")' db upgrade
   ```

4. Verify the app is running:

   ```bash
   curl -i http://localhost:8000/
   ```

   Expected result: `HTTP/1.1 200 OK` with body `ok`.

5. Shut down and restart:

   ```bash
   docker compose down
   docker compose up --build
   ```

   Hit `http://localhost:8000/` again to confirm the app still starts. Database data is stored in the `db_data` named volume.