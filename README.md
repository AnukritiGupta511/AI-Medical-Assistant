# AI Medical Assistant

An intelligent AI-powered web application for medical information comprehension, educational diet/lifestyle recommendations, and medical report summarization using OCR and RAG.

> **Disclaimer**: This application is for **Educational Purposes Only** and is not a substitute for professional medical advice, diagnosis, or treatment. It should never be used for definitive diagnoses or emergency medical recommendations.

## Tech Stack
- **Backend**: FastAPI, PostgreSQL, Redis, ChromaDB, LangChain, Celery.
- **Frontend**: React, TypeScript, Tailwind CSS, Vite.
- **Infrastructure**: Docker, Docker Compose.

## Setup Instructions (Native)

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in the AI API keys:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies and start the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8080
   ```
4. Install dependencies and start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. Access the frontend at `http://localhost:5173` (or the port Vite provides) and backend API documentation at `http://localhost:8080/docs`.
