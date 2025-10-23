echo "Starting GTMForge with Google Cloud credentials..."

# export GOOGLE_APPLICATION_CREDENTIALS="secrets/gtmforge-475520-72b5724c3360.json"
export GCP_PROJECT_ID="gtmforge-475520"
export GCS_BUCKET_NAME="gtmforge-assets"
export VERTEX_AI_LOCATION="us-central1"

# API Mode: "true" for mock (free/fast), "false" for real APIs (costs money/slow)
export USE_MOCK_APIS="${USE_MOCK_APIS:-false}"  # Default to real APIs

# if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
#     echo "Error: Credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS"
#     exit 1
# fi

echo "Credentials loaded from: $GOOGLE_APPLICATION_CREDENTIALS"
echo "Project ID: $GCP_PROJECT_ID"
echo USE_MOCK_APIS=false
echo ""
if [ "$USE_MOCK_APIS" = "false" ]; then
echo "🎨 Real Imagen API: ENABLED (costs ~\$0.04 per image)"
echo "🎬 Real Veo API: ENABLED (costs ~\$0.20 per video, takes 30-60s)"
if [ -n "$CANVA_API_KEY" ]; then
    echo "📊 Real Canva API: ENABLED"
else
    echo "📊 Real Canva API: DISABLED (no API key)"
fi
else
    echo "🎨 Mock Imagen: FREE & FAST"
    echo "🎬 Mock Veo: FREE & FAST"
    echo "📊 Mock Canva: FREE & FAST"
fi
echo ""
echo "Starting FastAPI backend on http://localhost:8000"
python api.py

