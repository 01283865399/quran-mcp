# Manual Deployment

## 1. Push the project to GitHub

1. Create a new empty repository on GitHub.
2. Open PowerShell in the project root:

```powershell
git init
git add .
git commit -m "Build Quranic religious website"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Do not commit `.env`, API keys, database passwords, or private certificates. The repository already ignores `.env`.

## 2. Deploy the backend

The Python MCP backend needs a Python/container host, PostgreSQL for full persistence, and optional GoodMem/LLM credentials. Vercel is not the right host for this long-running FastMCP server.

Use one of these options:

- Docker host: run `docker compose up -d --build` after setting `.env`.
- Railway, Render, Fly.io, or a VPS: deploy the `Dockerfile` and expose port `8088`.

Record the public backend URL, for example:

```text
https://api.example.com
```

Confirm these URLs work before deploying the frontend:

```text
https://api.example.com/.health
https://api.example.com/api/quran?ayah=1:1
```

## 3. Deploy the frontend to Vercel

1. Open Vercel and choose **Add New Project**.
2. Import the GitHub repository.
3. Set **Root Directory** to `frontend`.
4. Framework preset: **Vite**.
5. Build command: `npm run build`.
6. Output directory: `dist`.
7. Add an Environment Variable:

```text
Name: VITE_API_URL
Value: https://api.example.com
Environment: Production, Preview, Development
```

8. Deploy.

The Vercel build uses `frontend/vite.config.ts` and automatically writes a standalone `dist/landing.html`. `frontend/vercel.json` rewrites browser routes such as `/quran`, `/search`, `/adhkar`, and `/tasbih` to that shell.

## Local development

For same-origin local hosting, leave `VITE_API_URL` empty:

```powershell
cd frontend
npm install
npm run build
cd ..
.\.venv\Scripts\python.exe -m quran_mcp
```

Open `http://localhost:8088/`.

For a separately running frontend dev server, create `frontend/.env.local`:

```text
VITE_API_URL=http://localhost:8088
```

Never commit `.env.local`.
