# 🗂️ TailorTalk AI — Conversational Google Drive Discovery Agent

<div align="center">

![Banner](https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:312e81,100:7c3aed&height=220&section=header&text=TailorTalk%20AI&fontSize=52&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Conversational%20Google%20Drive%20Intelligence&descAlignY=58&descSize=20)

### ⚡ AI-Powered File Discovery using LangGraph, FastAPI, LangChain & Google Drive API

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-blueviolet?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-Tools-green?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![Google Drive](https://img.shields.io/badge/Google%20Drive-API-4285F4?style=for-the-badge&logo=google-drive)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render)

</div>

---

## 🧠 What is TailorTalk AI?

TailorTalk AI is a conversational Google Drive agent. You talk to it in plain English — it searches your Drive and returns real files instantly.

No more manually browsing folders. Just ask.

```
Show all PDFs
Find invoices from 2024
Search finance documents
List spreadsheets
Find images uploaded recently
```

---

## 🌐 Live Deployment

### 🖥️ Frontend (Streamlit)
**https://tailortalk-ai-drive-agent.streamlit.app/**

### ⚙️ Backend API (Render)
**https://tailortalk-ai-drive-agent.onrender.com/**

### 📦 GitHub Repository
**https://github.com/Shalmankursheeth/tailortalk-ai-drive-agent**

---

## 📸 Demo

> Chat with your Google Drive in plain English

![Chat UI — PDF Results](https://your-screenshot-link-1.png)
![Chat UI — Spreadsheet Results](https://your-screenshot-link-2.png)

> 💡 Replace the above links with actual screenshots from your Streamlit app for a premium look!

---

## 🏗️ Architecture

```
User Message
     │
     ▼
 Streamlit Frontend
     │
     ▼
 FastAPI Backend
     │
     ▼
 LangGraph Agent
     │
     ├── drive_search      → Search by query/type/date
     ├── list_all_files    → List all files recursively
     └── get_file_details  → Find specific file by name
     │
     ▼
 Google Drive API v3
     │
     ▼
 Formatted Results → User
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (`llama-3.1-8b-instant`) |
| Agent Framework | LangGraph + LangChain |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Drive Integration | Google Drive API v3 |
| Auth | Google Service Account |
| Deployment | Render + Streamlit Cloud |

---

## 📁 Project Structure

```
tailortalk/
├── backend/
│   ├── agent.py          # LangGraph agent + Drive tools
│   ├── main.py           # FastAPI server
│   └── requirements.txt
├── frontend/
│   └── app.py            # Streamlit chat UI
└── README.md
```

---

## 🚀 Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/Shalmankursheeth/tailortalk-ai-drive-agent.git
cd tailortalk-ai-drive-agent
```

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Add environment variables

Create a `.env` file in `/backend`:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id
SERVICE_ACCOUNT_FILE=service_account.json
```

### 4. Add your service account

Place your `service_account.json` file in the `/backend` folder.

> Make sure the service account email has **Viewer** access to your Google Drive folder.

### 5. Run the backend

```bash
uvicorn main:app --reload
```

### 6. Run the frontend

```bash
cd frontend
streamlit run app.py
```

---

## ☁️ Render Deployment

1. Push code to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Set environment variables:
   - `GROQ_API_KEY`
   - `GOOGLE_DRIVE_FOLDER_ID`
   - `SERVICE_ACCOUNT_FILE` = `/etc/secrets/service_account.json`
4. Upload `service_account.json` as a **Secret File** at `/etc/secrets/service_account.json`
5. Deploy 🎉

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/chat` | Send message to agent |
| GET | `/drive-test` | Test Drive connection |

### `/chat` Request

```json
{
  "message": "find all invoice PDFs",
  "history": []
}
```

### `/chat` Response

```json
{
  "response": "Found 3 file(s):\n\n**Spinny invoice.docx**\n..."
}
```

---

## 🤖 How the Agent Works

1. User sends a natural language message via Streamlit
2. LangGraph agent passes it to Groq LLM
3. LLM decides which tool to call (`drive_search`, `list_all_files`, or `get_file_details`)
4. Tool converts the request into a valid Google Drive API query
5. Results are formatted and returned to the user

---

## 📄 License

MIT License — free to use and modify.

---

<div align="center">

Built with ❤️ using LangGraph · LangChain · FastAPI · Groq · Google Drive API

</div>
