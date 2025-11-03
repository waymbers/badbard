# Form a Pauper Backend

This directory contains the FastAPI backend for Form a Pauper. The service allows administrators to craft dynamic aid request templates and collect submissions that are validated against the defined field requirements.

## Features

- CRUD endpoints for managing form templates
- Validation of submissions based on template field definitions
- SQLite persistence via SQLModel
- CORS enabled for easy integration with front-end clients
- Simple health check endpoint

## Requirements

- Python 3.10+

## Installation

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment.

3. Install dependencies with `pip`:

   ```bash
   pip install -e .
   ```

   Or using the provided `pyproject.toml`:

   ```bash
   pip install .
   ```

4. Install test dependencies:

   ```bash
   pip install .[test]
   ```

## Running the Server

Use Uvicorn to start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive documentation is available at `/docs`.

## Environment Variables

- `FORMAPauper_API_V1_PREFIX`: Override the API prefix (default `/api/v1`).
- `FORMAPauper_DATABASE_URL`: Provide a custom database URL. Defaults to a SQLite file in the repository.
- `FORMAPauper_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins.

## Running Tests

```bash
pytest
```
