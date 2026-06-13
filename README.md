# ChatPDF 📄

Chat with any PDF using AI. Upload a document, ask questions about it, and get intelligent answers powered by Google Gemini.

---

## What It Does

- Upload any PDF and start a conversation with it
- **Search inside PDF** — finds exact answers from the document using RAG and vector search
- **Analytical Questions** — understands the full document context to answer broader questions
- Saves all chat history so you can revisit previous conversations
- JWT authentication and Google OAuth login

---

## Architecture

<img width="1488" height="960" alt="Architecture" src="https://github.com/user-attachments/assets/b39aefe3-6aad-4dfd-9f52-129996ab68d0" />


---

## Tech Stack

**Backend**
- FastAPI + Python
- LangChain for RAG pipeline
- ChromaDB for vector storage
- Google Gemini API for LLM and embeddings
- PostgreSQL for data storage
- Redis for summary caching
- JWT + Google OAuth for authentication

**Frontend**
- Vanilla HTML, CSS, JavaScript


---

## Folder Structure
```text
ChatPDF/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.py          # Register, login, Google OAuth endpoints
│   │   │   ├── documents.py     # PDF upload and listing endpoints
│   │   │   ├── sessions.py      # Chat session create, list, close endpoints
│   │   │   └── chat.py          # Chat endpoint and history retrieval
│   │   │
│   │   ├── core/
│   │   │   ├── rag.py           # Vector search and RAG answer generation
│   │   │   ├── embeddings.py    # Gemini embedding generation
│   │   │   └── summariser.py    # LangChain summarisation with Redis caching
│   │   │
│   │   ├── db/
│   │   │   ├── database.py      # PostgreSQL connection and session setup
│   │   │   ├── models.py        # SQLAlchemy models and Pydantic schemas
│   │   │   └── crud.py          # Database read/write operations
│   │   │
│   │   ├── config.py            # Environment variables and model factories
│   │   └── main.py              # FastAPI entry point and route registration
│   │
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   │
│   ├── index.html               # Login & registration page
│   ├── dashboard.html           # PDF upload and session dashboard
│   ├── chat.html                # Chat interface with mode selection
│   ├── style.css                # Global dark-theme styling
│   │
│   └── js/
│       ├── api.js               # API calls and JWT handling
│       ├── auth.js              # Authentication & Google OAuth
│       ├── dashboard.js         # Uploads and session management
│       ├── chat.js              # Chat interactions and messaging
│       └── utils.js             # Shared utility functions
│
└── .gitignore
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/Swaroop883/ChatPDF.git
cd ChatPDF
```

**2. Create and activate virtual environment**
```bash
python -m venv chatpdf-env

# Windows
chatpdf-env\Scripts\activate

# Mac/Linux
source chatpdf-env/bin/activate
```

**3. Install dependencies**
```bash
pip install -r backend/requirements.txt
```

**4. Create a `.env` file in the root folder with the following content**

Get your free Gemini API key from [aistudio.google.com](https://aistudio.google.com). No model downloads needed — everything runs via API calls.

```
LLM_PROVIDER=gemini
LLM_MODEL_NAME=gemini-1.5-flash
LLM_API_KEY=your_gemini_api_key_here

EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL_NAME=models/embedding-001

DATABASE_URL=postgresql://your_user:your_password@localhost/chatpdf
JWT_SECRET_KEY=any_long_random_string_here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

REDIS_URL=redis://localhost:6379
```

**5. Make sure PostgreSQL and Redis are running on your machine**

**6. Run the backend**
```bash
cd backend
uvicorn app.main:app --reload
```

**7. Open the frontend**

Open `frontend/index.html` in your browser or use Live Server in VS Code.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/google` | Login with Google OAuth |
| POST | `/document/upload` | Upload and process a PDF |
| GET | `/document/list` | List all uploaded documents |
| POST | `/session/create` | Create a new chat session |
| GET | `/session/list` | List all chat sessions |
| POST | `/chat` | Send a question and get an answer |
| GET | `/history/{session_id}` | Get full chat history for a session |
| DELETE | `/session/close/{session_id}` | Close session and clean up vectors |

---

## Author

Built by **Swaroop** 
