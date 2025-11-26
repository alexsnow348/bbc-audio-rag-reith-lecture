# Frontend Structure

This will contain the Svelte 5 frontend with Bit UI and Tailwind CSS.

## Directory Structure (Planned)

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ui/              # Reusable UI components (Bit UI)
│   │   │   ├── downloads/       # Download feature components
│   │   │   ├── transcripts/     # Transcript feature components
│   │   │   ├── reader/          # PDF reader components
│   │   │   ├── chat/            # Chat interface components
│   │   │   └── history/         # History view components
│   │   ├── api/                 # API client functions
│   │   ├── stores/              # Svelte stores for state management
│   │   ├── types/               # TypeScript type definitions
│   │   └── utils/               # Utility functions
│   ├── routes/                  # SvelteKit routes
│   │   ├── +layout.svelte       # Root layout
│   │   ├── +page.svelte         # Home page
│   │   ├── downloads/
│   │   ├── transcripts/
│   │   ├── reader/
│   │   ├── chat/
│   │   └── history/
│   ├── app.css                  # Global styles
│   └── app.html
├── static/
├── package.json
├── svelte.config.js
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Tech Stack

- **Svelte 5**: Latest version with runes
- **Bit UI**: Headless component library
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type safety
- **TanStack Query**: Data fetching and caching
- **Axios**: HTTP client

## Setup Instructions

Coming soon...
