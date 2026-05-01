# AI-HCP CRM - Healthcare Professional Interaction Logging Module

## Project Overview
AI-HCP CRM is a full-stack application designed for medical sales representatives to log interactions with Healthcare Professionals (HCPs). The system offers two interaction methods:
1. **Structured Form** - Traditional data entry form
2. **AI Conversational Chat** - Natural language interface powered by LangGraph and Groq LLM

## Tech Stack

### Frontend
- **React** - UI library
- **Redux Toolkit** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Google Inter Font** - Typography

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **PostgreSQL/MySQL** - Database
- **LangGraph** - AI workflow orchestration
- **Groq API** - LLM integration (gemma2-9b-it model)

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL or MySQL

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create `.env` file in backend directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key_here
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
ai-hcp-crm/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InteractionForm.jsx
│   │   │   ├── AIChat.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── Toast.jsx
│   │   ├── pages/
│   │   │   └── Home.jsx
│   │   ├── redux/
│   │   │   ├── store.js
│   │   │   ├── interactionSlice.js
│   │   │   └── chatSlice.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   └── interaction.py
│   ├── schemas/
│   │   └── interaction.py
│   ├── routes/
│   │   └── interaction.py
│   ├── agents/
│   │   └── crm_agent.py
│   ├── tools/
│   │   ├── log_interaction.py
│   │   ├── edit_interaction.py
│   │   ├── summarize_interaction.py
│   │   ├── followup_recommendation.py
│   │   └── hcp_history.py
│   ├── services/
│   │   └── groq_service.py
│   ├── main.py
│   └── requirements.txt
│
├── README.md
└── requirements.txt
```

## API Endpoints

### Interaction Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interaction` | Create new interaction |
| GET | `/api/interaction` | Get all interactions |
| GET | `/api/interaction/{id}` | Get interaction by ID |
| PUT | `/api/interaction/{id}` | Update interaction |
| DELETE | `/api/interaction/{id}` | Delete interaction |

### AI Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | Process AI chat message |

## LangGraph Workflow

The LangGraph workflow orchestrates AI interactions through the following flow:

```
User Input → Router Node → Tool Selection → Groq LLM → Database → Response
```

### Available Tools

1. **Log Interaction Tool**
   - Saves structured interaction data
   - Extracts entities from natural language
   - Generates clean summary

2. **Edit Interaction Tool**
   - Updates existing interaction records
   - Modifies fields dynamically

3. **Summarize Interaction Tool**
   - Generates concise visit summaries

4. **Follow-Up Recommendation Tool**
   - Suggests next actions (e.g., send brochure, schedule visit)

5. **HCP History Tool**
   - Fetches previous interaction history
   - Shows trends and previous meetings

## AI Tool Explanation

### LangGraph Agent
The CRM Agent is a stateful workflow that:
- Receives user messages
- Determines intent using Groq LLM
- Routes to appropriate tool
- Processes tool output
- Returns formatted response

### Groq Integration
- Uses `gemma2-9b-it` model for natural language understanding
- API keys stored in environment variables
- Async requests for better performance

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key_here
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## How to Run

### Running Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Frontend
```bash
cd frontend
npm run dev
```

### Access the Application
- Frontend: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs`
- API ReDoc: `http://localhost:8000/redoc`

## Sample Interaction Data

The system includes realistic sample data for testing:

```json
{
  "hcp_name": "Dr. Sarah Johnson",
  "interaction_type": "In-Person Visit",
  "discussion_notes": "Discussed new diabetes medication benefits...",
  "sentiment": "Positive",
  "summary": "Productive meeting with Dr. Johnson about new diabetes treatment options.",
  "follow_up": "Send clinical trial data next week"
}
```

## Features

- Structured interaction form with validation
- AI conversational chat interface
- LangGraph-powered AI agent
- Groq LLM integration
- Redux state management
- Responsive CRM dashboard
- Toast notifications
- Loading states
- Error handling

## License

MIT License
