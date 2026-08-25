# Sprout

A gamified habit tracker. Log any goal you're building consistency on
gym, coding, gaming, reading, anything and watch a retro pixel art
garden grow tile by tile with every entry. Miss a day and it wilts a
little. Every week, Sprout generates a shareable pixel-art recap
card summarizing your streak and progress, built to post anywhere.

## Why

Most habit trackers are glorified checklists. The same reward loop
that makes doomscrolling hard to put down a small hit of "just one
more" — is what makes games sticky too. Sprout borrows that loop
(streaks, growth, shareable progress) and points it at real habits
instead of infinite scroll.

## Tech stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (SQLite for local development)
- **Auth**: JWT-based email/password login

## Status

Early development MVP in progress.

## Running locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
