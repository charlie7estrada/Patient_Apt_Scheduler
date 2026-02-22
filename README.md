# Patient Appointment Scheduler

A full-stack web application that lets patients book appointments with their healthcare providers through an AI-powered chat interface.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | JavaScript, React, Vite |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| AI | Claude API |
| Deployment | Render (backend), Vercel (frontend) |

## Features (Planned)

- AI chat interface for natural-language appointment booking
- Patient and provider authentication (JWT)
- Provider availability management
- Appointment history and upcoming visit dashboard
- Real-time chat with streaming responses

## Project Structure

```
Patient-Apt-Scheduler/
├── backend/          # FastAPI application
│   └── app/
│       ├── main.py
│       ├── models/
│       ├── routes/
│       └── services/
├── frontend/         # React + Vite application
│   ├── src/
│   └── public/
└── README.md
```

## Roadmap

- [x] Phase 1 — Project foundation & repo setup
- [ ] Phase 2 — Core data models & authentication
- [ ] Phase 3 — AI chatbot integration
- [ ] Phase 4 — Frontend UI
- [ ] Phase 5 — Polish & deployment

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in `/backend`:

```
DATABASE_URL=
SECRET_KEY=
AI_API_KEY=
```
