# Quranic Website Frontend

This folder contains the user-facing Arabic religious website for Rushd — رُشد.

## Development

```powershell
cd frontend
npm install
npm run build
```

The Vite build emits `src/quran_mcp/assets/landing.html`. The Python backend serves that file at `/` and exposes the browser Quran route at `/api/quran`.

## Structure

- `src/AppNew.svelte`: Quran reader, search, tafsir and hadith views.
- `src/landing-global.css`: frontend design system and responsive layout.
- `src/main.ts`: Svelte entry point.
- `landing.html`: Vite HTML shell.
