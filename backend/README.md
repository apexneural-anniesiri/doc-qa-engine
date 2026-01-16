# Document Q&A Engine - Backend

Backend server for the Document Q&A Engine using Python FastAPI, uvicorn, GroundX, and OpenAI.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or with virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

3. Edit `.env` with your actual API keys:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROUNDX_API_KEY`: Your GroundX API key
- Adjust `GROUNDX_BASE_URL` and paths if your GroundX instance uses different endpoints

## Running

Development (with auto-reload):
```bash
uvicorn main:app --reload --port 3001
```

Or:
```bash
python -m uvicorn main:app --reload --port 3001
```

Production:
```bash
uvicorn main:app --host 0.0.0.0 --port 3001
```

Server runs on `http://localhost:3001` by default (configurable via `PORT` in `.env`).

## API Endpoints

### POST /api/upload
Upload a PDF file for ingestion.

**Request**: `multipart/form-data` with field name `file`

**Response**:
```json
{
  "bucket_id": "string",
  "status": "processing|ready|failed"
}
```

### GET /api/status?bucket_id=...
Check ingestion status.

**Response**:
```json
{
  "bucket_id": "string",
  "status": "processing|ready|failed",
  "progress": number|null
}
```

### POST /api/chat
Ask a question about the document.

**Request**:
```json
{
  "question": "string",
  "bucket_id": "string"
}
```

**Response**:
```json
{
  "answer": "string",
  "sources": [
    {
      "text": "string",
      "page": number|null,
      "score": number|null
    }
  ]
}
```

## GroundX Configuration

The GroundX integration is in `groundx.py`. You may need to adjust:

1. **API Endpoints**: Update `GROUNDX_BASE_URL` and path constants in `.env` or `groundx.py`
2. **Response Mapping**: The code includes comments indicating where to adjust field mappings based on your GroundX API response shape
3. **Request Payloads**: The search request body may need adjustment based on GroundX API requirements

## File Size Limits

Default maximum file size is 50MB. Adjust `MAX_SIZE` in `main.py` if needed.

## Troubleshooting

- **CORS errors**: Ensure frontend URL is in the CORS origin list in `main.py`
- **API key errors**: Verify `.env` file exists and contains valid keys
- **GroundX errors**: Check API endpoint URLs and response format matches expected shape
- **Large file uploads**: If uploads fail, check uvicorn timeout settings and increase `MAX_SIZE` if appropriate
