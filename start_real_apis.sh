#!/bin/bash
# Force REAL APIs - no mocks!

echo "🚀 Starting GTMForge with REAL APIs (Imagen + Veo)"
echo "💰 WARNING: This will cost money (~\$0.64 per run)"
echo ""

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="secrets/gtmforge-475520-72b5724c3360.json"
export GCP_PROJECT_ID="gtmforge-475520"
export GCS_BUCKET_NAME="gtmforge-assets"
export VERTEX_AI_LOCATION="us-central1"

# FORCE REAL APIs
unset USE_MOCK_APIS
export USE_REAL_APIS="true"

# Check credentials file exists
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ Error: Credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS"
    exit 1
fi

echo "✅ Credentials: $GOOGLE_APPLICATION_CREDENTIALS"
echo "✅ Project: $GCP_PROJECT_ID"
echo "✅ Mode: REAL APIs ENABLED"
echo ""
echo "🎨 Imagen will generate REAL images (~\$0.04 each × 11 = \$0.44)"
echo "🎬 Veo will generate REAL video (~\$0.20, takes 30-60s)"
echo "📊 Canva will use mock (no API key)"
echo ""
echo "Starting backend on http://localhost:8000..."
echo ""

# Run with python directly
python api.py


