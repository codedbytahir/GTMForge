# GTMForge - Quick Start Guide

## 🚀 Ready to Test Real APIs!

Everything is configured and ready. You can now toggle between **mock** and **real** APIs.

---

## Option 1: Test with Mock APIs (FREE, INSTANT)

```bash
export USE_MOCK_APIS=true
python test_real_apis.py
```

**What you'll see:**
- ✅ Mock Imagen: Tiny placeholder images
- ✅ Mock Veo: Tiny placeholder videos  
- ✅ Mock Canva: Deck IDs without real URLs
- ⚡ Instant generation
- 💰 $0 cost

---

## Option 2: Test with Real APIs (COSTS MONEY)

### Step 1: Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com --project=gtmforge-475520
```

### Step 2: Run Test

```bash
export USE_MOCK_APIS=false
python test_real_apis.py
```

**What you'll see:**
- 🎨 Real Imagen: Professional AI-generated image (~$0.04)
- 🎬 Real Veo: AI-generated video (~$0.20, takes 30-60s)
- 📊 Mock Canva: Still mocked (no API key yet)
- 💰 Total: ~$0.24 for this test

---

## Option 3: Run Full System

### With Mock APIs (Default):

```bash
export USE_MOCK_APIS=true
./start.sh  # Backend on :8000

# In another terminal:
cd web && npm run dev -- -p 3001  # Frontend on :3001
```

### With Real APIs:

```bash
# Enable APIs first (one-time setup)
gcloud services enable aiplatform.googleapis.com --project=gtmforge-475520

# Start backend with real APIs
export USE_MOCK_APIS=false
./start.sh

# In another terminal:
cd web && npm run dev -- -p 3001
```

Then open http://localhost:3001 and submit an idea!

---

## What Gets Generated

### Mock Mode (USE_MOCK_APIS=true):
- 📁 `/output/assets/images/` - 11 tiny placeholder files
- 📁 `/output/assets/videos/` - 1 tiny placeholder file
- 💰 Cost: $0
- ⏱️  Time: < 1 second

### Real Mode (USE_MOCK_APIS=false):
- 📁 `/output/assets/images/` - 11 real AI-generated images (~500KB-2MB each)
- 📁 `/output/assets/videos/` - 1 real AI-generated video (~5-15MB)
- 💰 Cost: ~$0.64 per run
- ⏱️  Time: 30-90 seconds (mostly Veo)

---

## Troubleshooting

### "Module 'aiohttp' not found"

```bash
# Option 1: Install it
pip install aiohttp pillow

# Option 2: Use mock mode
export USE_MOCK_APIS=true
```

### "Real API failed, falling back to mock"

Check logs for:
- Is Vertex AI API enabled?
- Are credentials valid?
- Is service account authorized?

See `SETUP_REAL_APIS.md` for detailed troubleshooting.

---

## Cost Control

Set `USE_MOCK_APIS=true` anytime to stop spending money:

```bash
export USE_MOCK_APIS=true  # Safe mode: no API calls
./start.sh
```

---

## Next Steps

1. ✅ **Test mock mode first**: `export USE_MOCK_APIS=true && python test_real_apis.py`
2. ✅ **Enable Vertex AI**: `gcloud services enable aiplatform.googleapis.com`
3. ✅ **Test real mode**: `export USE_MOCK_APIS=false && python test_real_apis.py`
4. ✅ **Run full system**: `./start.sh` + frontend
5. ✅ **Generate your first deck!**

---

## Files Changed

- ✅ `app/utils/real_api_clients.py` - Real API implementations with fallback
- ✅ `app/agents/imagen_agent/agent.py` - Uses RealImagenClient
- ✅ `app/agents/veo_agent/agent.py` - Uses RealVeoClient
- ✅ `app/agents/canva_agent/agent.py` - Uses RealCanvaConnectClient
- ✅ `start.sh` - Shows API mode on startup
- ✅ `test_real_apis.py` - Quick test script
- ✅ `api.py` - Serves local assets at `/assets/`

**All automatic!** Just toggle `USE_MOCK_APIS` and go! 🚀


