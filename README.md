# TailorTalk Drive Assistant

A conversational AI agent that searches Google Drive files via natural language.

## 🏗️ Project Structure
```
tailortalk/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── agent.py             # LangChain agent + Drive tools
│   ├── service_account.json # ← You add this!
│   ├── requirements.txt
│   └── .env                 # ← You create this!
└── frontend/
    ├── app.py               # Streamlit chat UI
    └── requirements.txt
```

---

## 🚀 Local Setup

### 1. Clone & Setup Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
# Place your service_account.json in this folder
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501

---

## ☁️ Deploy to Render (Backend)

1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Set:
   - Root directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GROQ_API_KEY` = your key
6. Also upload `service_account.json` as a Secret File

## ☁️ Deploy Frontend (Streamlit Cloud)

1. Go to share.streamlit.io
2. Connect GitHub → select `frontend/app.py`
3. Add secret: `BACKEND_URL = https://your-render-url.onrender.com`

---

## 🔍 Example Queries

- "Show me all PDF files"
- "Find files about finance"
- "List files modified in the last month"
- "Find images"
- "Search for reports from 2024"

---

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **Agent**: LangChain + tool calling
- **LLM**: Groq (llama-3.3-70b)
- **Integration**: Google Drive API v3
- **Frontend**: Streamlit
