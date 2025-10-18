# GTMForge

**Multi-Agent AI System for Go-To-Market Automation**

GTMForge is a sophisticated multi-agent AI system built with **Google's Agent Development Kit (ADK)** that automates the creation of comprehensive go-to-market materials using Google's latest AI technologies including **Gemini 2.0**, **Vertex AI**, **Imagen**, and **Veo**.

> **Current Status:** Phase 0 - Pre-Build Setup ✅  
> **Next Phase:** Phase 1 - Foundation Build (Core Agent Development)

---

## Project Vision

GTMForge orchestrates multiple specialized AI agents to transform startup ideas into polished GTM assets:

- **Ideation Agent**: Expands user input into ICPs, pain points, and context
- **Comparative Insight Agent**: Benchmarks ideas vs. successful startups
- **Pitch Writer Agent**: Builds slide narratives and talking points
- **Prompt Forge Agent**: Generates and refines prompts for Imagen/Veo
- **QA Agent**: Ensures validity of assets and compliance
- **Publisher Agent**: Combines outputs into deliverable manifests

---

## Project Structure

```
GTMForge/
├── app/
│   ├── agents/     # Agent implementations
│   ├── core/       # ADK orchestration engine
│   └── utils/      # Helper functions and utilities
├── frontend/       # Web UI (React/Next.js/Vite)
├── prompts/        # AI prompt templates
├── output/
│   ├── images/     # Generated images from Imagen
│   └── videos/     # Generated videos from Veo
├── main.py         # CLI entry point
├── api.py          # FastAPI backend server
├── requirements.txt
├── .env.template
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Google Cloud Project** with Vertex AI enabled
- **Gemini 2.0 API** access (Pro, Flash, Imagen, Veo)
- **Google Cloud Storage** bucket (for asset hosting)
- **Canva Connect API** access (optional, Phase 2+)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DanielJEfres/GTMForge.git
   cd GTMForge
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys and configuration
   ```

### Configuration

Edit `.env` file with your credentials:

- **GCP_PROJECT_ID**: Your Google Cloud project ID
- **GOOGLE_APPLICATION_CREDENTIALS**: Path to service account JSON
- **GEMINI_API_KEY**: Gemini 2.0 API key
- **VERTEX_AI_PROJECT**: Vertex AI project configuration
- **GCS_BUCKET_NAME**: Google Cloud Storage bucket for assets

Refer to `.env.template` for complete configuration options.

---

## Build Phases

### Phase 0 - Pre-Build Setup 
- [x] Access + API Keys configuration
- [x] Environment setup (`.env.template`)
- [x] Repository structure created
- [x] Dependencies defined
- [x] `.gitignore` configured

### Phase 1 - Foundation Build (NEXT)
- [ ] Build ADK Orchestrator
- [ ] Define Core Agents (Ideation, Comparative Insight, Pitch Writer, Prompt Forge, QA)
- [ ] Implement MCP Integrations
- [ ] Test sequential agent flow

### Phase 2 - Generative Media Integration
- [ ] Imagen integration for slide visuals
- [ ] Veo integration for video generation
- [ ] Canva Connect API automation
- [ ] Prompt optimization loop

### Phase 3 - QA and System Integration
- [ ] End-to-end testing
- [ ] Publisher Agent implementation
- [ ] FastAPI backend with WebSocket support
- [ ] CLI entry point
- [ ] Validation across multiple ideas

### Phase 4 - Frontend, UX, and Documentation
- [ ] Modern web frontend (React/Next.js/Vite)
- [ ] Real-time generation dashboard
- [ ] Visual enhancements and branding
- [ ] Architecture diagrams (Excalidraw)
- [ ] Complete documentation and user guides

### Phase 5 - Bake-Off Readiness
- [ ] Live demo preparation
- [ ] Judging criteria alignment
- [ ] Final submission materials

---

## Technology Stack

- **Google ADK**: Multi-agent orchestration (sequential, parallel, loop)
- **Gemini 2.0**: LLM reasoning and content generation
- **Vertex AI**: Cloud AI platform
- **Imagen**: Image generation
- **Veo 3.1**: Video generation
- **Google Cloud Storage**: Asset hosting
- **Canva Connect API**: Presentation automation (Phase 2+)

---

## Documentation

- **`implementation.md`**: Complete implementation roadmap
- Architecture diagrams: Coming in Phase 4
- Agent specifications: Coming in Phase 1

---

## Contributing

This project is part of the **Google Cloud AI Bake-Off** and is currently in active development.

1. Follow the implementation roadmap in `implementation.md`
2. Maintain folder structure and naming conventions
3. Add tests for new functionality
4. Keep documentation updated

---

## Team

**Author:** Daniel Efres  
**Collaborator:** Luis Sala (Google Cloud)  
**Codename:** GTMForge  
**Event:** Google Cloud AI Bake-Off 2025

---

## Links

- [Google ADK Documentation](https://cloud.google.com/agent-builder/docs)
- [Vertex AI](https://cloud.google.com/vertex-ai)
- [Gemini API](https://ai.google.dev/)
- [Imagen Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
- [Veo Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/video/overview)
