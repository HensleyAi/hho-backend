# Hensley Home Office Backend v1

FastAPI backend for Hensley Home Office using Postgres (or SQLite locally), designed to run on Render.

## Features

- Users, accounts, statements, transactions, income events
- Statement upload endpoint (metadata only for v1)
- Bulk transaction insert
- Monthly summary endpoint
- Simple projection placeholder
- AI insights endpoint (requires OPENAI_API_KEY)

## Running locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (optional):

   ```bash
   export DATABASE_URL=sqlite:///./hho.db
   export OPENAI_API_KEY=your_key_here
   ```

4. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://127.0.0.1:8000, and docs at http://127.0.0.1:8000/docs.

## Deploying to Render

1. Push this folder to a Git repository.
2. Create a new **Web Service** on Render, select the repo.
3. Use:

   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`

4. Set `DATABASE_URL` to your Render Postgres connection string.
5. Set `OPENAI_API_KEY` to your OpenAI API key.

