#!/bin/bash
# Setup script for Svelte + Bit UI + Tailwind migration

set -e

echo "🚀 Setting up Svelte Migration..."
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js and npm first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ npm found: $(npm --version)"
echo ""

# Navigate to svelte-migration directory
cd "$(dirname "$0")"

# Create frontend with Vite + Svelte + TypeScript
echo "📦 Creating Svelte frontend..."
npm create vite@latest frontend -- --template svelte-ts

cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install Tailwind CSS
echo "🎨 Installing Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install Bit UI and other dependencies
echo "🧩 Installing Bit UI and utilities..."
npm install bits-ui
npm install lucide-svelte
npm install @tanstack/svelte-query
npm install axios
npm install svelte-sonner
npm install clsx tailwind-merge

# Install development dependencies
echo "🛠️  Installing dev dependencies..."
npm install -D @sveltejs/adapter-node
npm install -D vite-plugin-tailwind-purgecss

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure Tailwind CSS (see MIGRATION_PLAN.md)"
echo "   2. Set up backend FastAPI"
echo "   3. Start development:"
echo "      cd frontend && npm run dev"
echo ""
