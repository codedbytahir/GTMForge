echo "Starting GTMForge Frontend..."

cd web
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "Starting Next.js frontend on http://localhost:3001"
npm run dev -- -p 3001

