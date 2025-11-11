# AI-Powered Stock Research Copilot

An intelligent stock research assistant powered by Perplexity AI that guides users through professional-grade equity analysis.

## Features

- **Guided Research Flow**: Step-by-step analysis (Overview → Financials → Moat → Risks → Memo)
- **Free Chat Mode**: Ask custom questions about any stock
- **Live Data**: Powered by Perplexity AI with real-time citations
- **Dynamic Prompts**: Structured templates with user input injection
- **Interactive UI**: Clean chatbot interface for seamless research

## Quick Start

### Backend Setup (Flask)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your PERPLEXITY_API_KEY to .env
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

- `PERPLEXITY_API_KEY`: Your Perplexity API key
- `PORT`: Backend server port (default: 3001)

## API Endpoints

- `POST /api/research/guided` - Execute guided research step
- `POST /api/research/chat` - Free-form chat query
- `GET /api/research/templates` - List available prompt templates

## Tech Stack

- Frontend: React + Vite
- Backend: Flask (Python)
- AI: Perplexity API
