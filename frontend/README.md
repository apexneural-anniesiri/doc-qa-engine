# Document Q&A Engine - Frontend

React + Vite + TypeScript frontend for the Document Q&A Engine.

## Setup

1. Install dependencies:
```bash
npm install
# or
bun install
```

2. Create a `.env` file (optional, defaults to `http://localhost:3001`):
```bash
VITE_API_URL=http://localhost:3001
```

## Running

Development:
```bash
npm run dev
# or
bun run dev
```

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

Frontend runs on `http://localhost:5173` by default.

## Features

- **Drag-and-drop PDF upload** with progress indicator
- **Real-time ingestion status polling** until document is ready
- **Modern dark-mode chat UI** with message bubbles
- **Source citations** with expandable sections showing retrieved chunks
- **Responsive design** for mobile and desktop
- **Accessibility** with reduced motion support

## API Integration

The frontend communicates with the backend API via typed fetch calls in `src/api.ts`. Ensure the backend is running and CORS is configured correctly.
