# Flask API Backend

## Setup

Clone the repository, create and activate a virtual environment, then install the project dependencies:

```bash
git clone <repository-url>
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the virtual environment with `.venv\Scripts\activate`.

## Environment variables

Copy `.env.example` to `.env` and fill in the values for your local environment:

```bash
cp .env.example .env
```

Do not commit `.env`; it may contain secrets.

## Migrations

The project uses Flask-Migrate for database schema changes. With the virtual environment active, apply the latest migrations with:

```bash
FLASK_APP='backend_project:create_app("development")' flask db upgrade
```

To create a migration after changing a model, run:

```bash
FLASK_APP='backend_project:create_app("development")' flask db migrate -m "describe the change"
```

Review generated migration files before applying them.
