# broken-deploy

A small notes API, packaged with Docker and Postgres. **It does not work.** Your job is to find out why and fix it.

This is the practice fixture for BE106 Unit 4, "Challenge: debugging a broken deploy". The application code is fine. Everything that is wrong is **configuration**: how the container starts, which environment variables it gets, and where it looks for its database. There is more than one problem, and each one only shows up after the previous one is fixed.

## What it should do when it works

```bash
docker compose up --build
```

Then, from a second terminal:

```bash
curl -i http://localhost:8000/health
# HTTP/1.1 200 OK   {"status": "ok"}

curl -i -X POST http://localhost:8000/notes -H "Content-Type: application/json" -d '{"text": "it works"}'
# HTTP/1.1 201 CREATED   {"id": 1, "text": "it works"}

curl -i http://localhost:8000/notes
# HTTP/1.1 200 OK   {"notes": [{"id": 1, "text": "it works"}]}
```

A note you created should still be there after `docker compose down` followed by `docker compose up`.

## The rules

1. **Do not change any file inside `notes/`.** The bugs are not in the Python code.
2. Diagnose before you change anything. For each problem, write down:
   - the symptom (status code, error body, or what curl printed),
   - where you looked (`docker compose ps`, `docker compose logs web`, `docker compose logs db`),
   - the cause.
3. Fix one problem at a time. Rebuild and re-test after each fix.
4. You are done when all three `curl` checks above pass and the note survives a restart.

## Tools you will need

```bash
docker compose ps              # is each container running, or has it exited?
docker compose logs web        # what did the app print when it started or failed?
docker compose logs db         # is the database up?
docker compose up --build      # rebuild after changing the Dockerfile
docker compose down            # stop everything (add -v to also delete the database volume)
```

Every error the app returns has the same shape: `{"error": {"code": "...", "message": "..."}}`. Read the code. It tells you which part of the system is failing.
