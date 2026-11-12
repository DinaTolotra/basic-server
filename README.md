# Caching Demo API

A FastAPI service for managing users, projects, and project items. Data is stored in PostgreSQL with SQLModel, and item records are cached in memory by the running API process.

## Requirements

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL

## Setup

Install the project dependencies:

```bash
uv sync
```

Create a PostgreSQL database, then copy `.env.exemple` to `.env` and set `DATABASE_URL` to a PostgreSQL connection string. For example:

```dotenv
DATABASE_URL=postgresql+psycopg://taskflow:change-me@localhost:5432/TaskFlow
```

The database server and the named database must already exist. The API creates its tables when it starts.

## Run

Start the development server:

```bash
uv run fastapi dev
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

## API

All collection endpoints accept `offset` (default `0`) and `limit` (default `100`, maximum `500`) query parameters.

| Resource | Create | List | Read | Update | Delete |
| --- | --- | --- | --- | --- | --- |
| Users | `POST /users` | `GET /users` | `GET /users/{user_id}` | `PUT /users/{user_id}` | `DELETE /users/{user_id}` |
| Projects | `POST /projects` | `GET /projects` | `GET /projects/{project_id}` | `PUT /projects/{project_id}` | `DELETE /projects/{project_id}` |
| Items | `POST /items` | `GET /items` | `GET /items/{item_id}` | `PUT /items/{item_id}` | `DELETE /items/{item_id}` |

Projects require an existing `owner_id`; items require an existing `project_id`. Item fields include `title`, `description`, `status` (default `TODO`), `priority` (0-2, default `1`), and an ISO 8601 `due_date`.

`GET /health` returns `{"status":"ok"}`. Responses include an `X-Process-Time` header with the server-side request duration. Item reads use a process-local cache, which is populated by item reads and list requests and updated or invalidated by item mutations.