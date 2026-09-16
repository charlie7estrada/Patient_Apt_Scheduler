# Patient Appointment Scheduler

A full-stack web application that lets patients book appointments with their healthcare providers through an AI-powered chat interface. Instead of filling out a booking form, the patient just talks to the assistant — it collects the date, time, and reason for the visit, then calls a backend tool to actually create the appointment.

**Live demo:** https://patient-apt-scheduler.vercel.app
**API:** https://patient-apt-scheduler-api.onrender.com

**Try it without an account:** click "Try the demo" on the login page. You get a demo patient with two sample appointments already booked, so you can reschedule or cancel right away. Demo accounts and their appointments are deleted after 24 hours.

> Note: the backend is hosted on Render's free tier, which spins down after inactivity. The first request after idle time can take 30–50 seconds to wake up — if the demo seems stuck on first load, give it a moment.


## Features
- AI chat interface for natural-language appointment booking, backed by real tool-calling (not just conversation)
- Chatbot is date/timezone-aware (Central Time) and confirms with the patient before cancelling anything
- Appointment date/time validated against clinic hours - no past-dated or after-hours bookings
- JWT-based patient authentication (register/login) with loading and error states
- One-click guest demo, no registration, seeded with sample appointments and cleaned up automatically
- Upcoming appointments dashboard, scoped per patient, with live status (pending/cancelled)
- Deployed end-to-end: FastAPI on Render, React on Vercel, Postgres on Neon

### Not yet built
- Provider-side dashboard (accepting/managing appointments — currently a single seeded demo provider handles all bookings)
- Appointment status beyond pending/cancelled (confirmed/completed are modeled but never set)
- Password reset flow

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | JavaScript, React, Vite, Tailwind CSS |
| Database | PostgreSQL (Neon), SQLAlchemy, Alembic |
| AI | Mistral API |
| Deployment | Render (backend), Vercel (frontend) |

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

## Demo accounts

"Try the demo" calls `POST /api/v1/auth/guest`, which creates a patient account with a random email and no usable password, then returns a JWT the same way login does. Each guest is seeded with two appointments in the next open slots on the provider's calendar, so the slots are never double-booked.

Guest accounts and their appointments are deleted 24 hours after creation. The purge runs at application startup.

If the assistant replies that it is getting more requests than it can handle, the demo has hit its AI provider rate limit. Appointments booked before that still show in the sidebar.
