# Quick Start Guide - Svelte Migration

## ✅ What's Ready

### Backend (FastAPI) - READY TO USE
The FastAPI backend structure is complete with all route stubs. Located in `backend/`.

### Frontend (Svelte) - NEEDS SETUP
You'll need to initialize the Svelte project with the commands below.

---

## 🚀 Setup Instructions

### Step 1: Set up FastAPI Backend

```bash
cd svelte-migration/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

### Step 2: Set up Svelte Frontend

```bash
cd svelte-migration

# Create Svelte project with Vite
npm create vite@latest frontend -- --template svelte-ts

# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install Bit UI and utilities
npm install bits-ui lucide-svelte @tanstack/svelte-query axios svelte-sonner clsx tailwind-merge

# Install dev dependencies
npm install -D @sveltejs/adapter-node vite-plugin-tailwind-purgecss
```

---

### Step 3: Configure Tailwind CSS

Create/update `frontend/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}
```

Update `frontend/src/app.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gradient-to-br from-slate-50 to-slate-100;
  }
}
```

---

### Step 4: Run Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 📁 Project Structure

```
svelte-migration/
├── backend/              ✅ COMPLETE
│   ├── api/
│   │   ├── main.py      # FastAPI app
│   │   └── routes/      # All API routes
│   ├── requirements.txt
│   └── README.md
│
└── frontend/            ⏳ RUN COMMANDS ABOVE
    ├── src/
    │   ├── lib/
    │   │   ├── components/
    │   │   ├── api/
    │   │   ├── stores/
    │   │   └── types/
    │   └── routes/
    ├── package.json
    └── tailwind.config.js
```

---

## 🎯 Next Steps After Setup

1. **Backend**: Implement TODO items in route handlers
2. **Frontend**: Create UI components (see MIGRATION_PLAN.md)
3. **Integration**: Connect frontend to backend API
4. **Testing**: Test all features

---

## 🔗 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Svelte Tutorial](https://svelte.dev/tutorial)
- [Bit UI Components](https://www.bits-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## ⚠️ Current Status

- ✅ FastAPI backend structure created
- ✅ All API routes defined
- ✅ CORS configured
- ⏳ Svelte frontend - awaiting npm setup
- ⏳ UI components - to be created
- ⏳ API integration - to be implemented

**The redesigned Gradio app is still running at http://localhost:7860 for immediate use!**
