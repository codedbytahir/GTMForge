echo "Starting GTMForge with Google Cloud credentials..."

export GOOGLE_APPLICATION_CREDENTIALS="secrets/gtmforge-475520-72b5724c3360.json"
export GCP_PROJECT_ID="gtmforge-475520"
export GCS_BUCKET_NAME="gtmforge-assets"
export VERTEX_AI_LOCATION="us-central1"

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Error: Credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS"
    exit 1
fi

echo "Credentials loaded from: $GOOGLE_APPLICATION_CREDENTIALS"
echo "Project ID: $GCP_PROJECT_ID"
echo "Starting FastAPI backend on http://localhost:8000"
python api.py

