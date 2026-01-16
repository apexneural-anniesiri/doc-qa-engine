# Quick Setup Commands

## 1. No External Database Needed!

The vector store uses a simple file-based system. No Docker or external services required!

## 2. Backend Setup (Python FastAPI)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the example or create manually:
# OPENAI_API_KEY=your_openai_api_key_here
# PORT=3001
# CHROMA_URL=http://localhost:8000  # Optional: leave empty for embedded mode

# Start development server
uvicorn main:app --reload --port 3001
```

Backend runs on: `http://localhost:3001`

## 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install
# or
bun install

# Start development server
npm run dev
# or
bun run dev
```

Frontend runs on: `http://localhost:5173`

## Required Environment Variables (backend/.env)

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=3001

# Vector Storage (optional)
VECTOR_STORAGE_DIR=./vector_storage
```

## Verify Installation

1. **Backend**: Should show `INFO: Uvicorn running on http://127.0.0.1:3001`
2. **Frontend**: Should open in browser at `http://localhost:5173`
3. **Test**: Upload a PDF and ask a question!

## Troubleshooting

**Backend won't start:**
- Make sure virtual environment is activated
- Check that `.env` file exists with `OPENAI_API_KEY`
- Verify Python version: `python --version` (should be 3.8+)

**PDF extraction errors:**
- Ensure PDF is not password-protected
- Try a different PDF to verify file isn't corrupted
- Check server logs for detailed error messages

**Embedding errors:**
- Verify `OPENAI_API_KEY` is correct
- Check OpenAI API quota/limits
