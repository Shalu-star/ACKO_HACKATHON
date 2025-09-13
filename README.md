# ACKO Hackathon Submission

## Project Overview

This project is a healthcare assistant platform designed for real-time patient-doctor interaction, transcription, and sentiment analysis. It consists of a Python backend (FastAPI) and a static HTML frontend.

---

## Features
- **Real-time transcription** using Whisper model
- **Sentiment analysis** of patient responses
- **Session management** for multiple rooms
- **WebSocket communication** for live updates
- **Simple, user-friendly frontend**

---

## Repository Structure
```
ACKO_HACKTHON/
├── backend/
│   ├── main.py
│   ├── question_engine.py
│   ├── requirements.txt
│   ├── sentiment_analyzer.py
│   ├── session_manager.py
│   ├── transcription_service.py
│   └── __pycache__/
└── Frontend/
    ├── index.html
    └── patient.html
```

---

## Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd Frontend
python -m http.server 8080
```

---

## Deployment
- You can deploy the backend using Render, Heroku, or any cloud provider supporting Python and Uvicorn.
- The frontend can be deployed as a static site on Vercel, Netlify, or similar platforms.

---

## How to Use
1. Open the frontend in your browser.
2. Join a room as a patient or doctor.
3. Speak or type your responses; transcription and sentiment analysis will be shown in real time.

---

## Team & Credits


---

## License
This project is for hackathon submission and educational purposes.
