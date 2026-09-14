# Getting Started

Tsubonote can be run locally using Python and Node.js, or with Docker Compose.

## Prerequisites

- Python 3.x
- Node.js / npm
- Docker Desktop (optional, recommended)
- PostgreSQL / Supabase database
- Google OAuth credentials if authentication is required
- Playwright Chromium browser

## Backend

`!!! Note: Make user the visit each db_manager file in dir :`[manage_db](../manage_db) `and execute the create func (including create_index) of each file to setup the database after setting up your environment.`

### Set Up Environment : 

Switch realestate_agent with your root dir. 

```bash
git clone https://github.com/dav404-cmd/realestate_agent.git
cd realestate_agent

python -m venv .venv

.venv/Scripts/Activate.ps1
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright's browser:

```bash
playwright install chromium
```

**Set up .env**

Copy the .env.example and filled the value as mentioned.

```bash
cp .env.example .env
```

Get jwt secret. Run the following bash and paste the provided value. 

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Run and customize :

`!!! for local hosting you will need few code changes in backend and frontend.`

Changes for local host : 

| file                            | line | changes                                                                                  |
|---------------------------------|------|------------------------------------------------------------------------------------------|
| [main_api](../apis/main_api.py) | 24   | inside allow_origins replace 'https://tsubonote.vercel.app' with 'http://localhost:5500' |
| [auth](../apis/auth.py)         | 75   | replace 'https://tsubonote.vercel.app' with 'http://localhost:5500/'                     |



```bash
uvicorn apis.main_api:app --reload
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend API URL through `.env` . Make a `.env` in your frontend dir and paste the following.
```text
PUBLIC_API_BASE=http://localhost:8000
API_BASE_INTERNAL=http://backend:8000
```

---

## Docker (Recommended)

Build and run 

```bash
docker compose up --build
```

Running prebuild docker 

```bash
docker compose up 
```

Close 

```bash
docker compose down 
```

`!! Note: The docker doesn't run airflow by default.`

Run with Airflow 

```bash
docker compose --profile airflow up 
```

Currently, the airflow only has some simple dags that request backend to run the scrapers and updaters on schedule and wait for the response.

---

## Project-Specific Configuration

The scraper, updater, AI agent, and other components have additional configuration options directly in their respective modules.

The getting-started guide intentionally covers only the configuration required to run the application. Developers who want to modify individual components should refer to the relevant module and its implementation.