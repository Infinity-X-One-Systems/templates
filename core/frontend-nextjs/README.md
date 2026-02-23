# Core Next.js Frontend Scaffold

Production-ready Next.js 15 frontend with PWA support, Tailwind CSS, React Query, and TypeScript strict mode.

## Quick Start

```bash
npm install
npm run dev
```

## PWA

PWA is enabled in production builds via `next-pwa`. The `public/manifest.json` configures app identity.

## Architecture

```
src/
├── app/             # Next.js App Router pages
│   ├── layout.tsx   # Root layout with PWA metadata
│   ├── page.tsx     # Home page
│   └── dashboard/   # Dashboard section
├── components/      # Reusable UI components
│   ├── providers.tsx # React Query + theme providers
│   └── dashboard/   # Dashboard-specific components
└── lib/
    └── api.ts       # Typed API client
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL (default: `http://localhost:8000`) |
