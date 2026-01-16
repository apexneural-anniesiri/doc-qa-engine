# Windows Installation Guide

## Problem: chroma-hnswlib Build Error

If you see:
```
error: Microsoft Visual C++ 14.0 or greater is required
```

This happens because ChromaDB's dependency `chroma-hnswlib` doesn't have pre-built wheels for Python 3.13 on Windows.

## Solution Options

### Option 1: Use Python 3.11 (Easiest - Recommended)

Python 3.11 has pre-built wheels for ChromaDB on Windows, so no build tools needed.

**Steps:**

1. **Install Python 3.11** (if not already installed):
   - Download from: https://www.python.org/downloads/release/python-3110/
   - During installation, check "Add Python to PATH"

2. **Create new virtual environment with Python 3.11:**
   ```bash
   cd backend
   py -3.11 -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip setuptools
   pip install -r requirements.txt
   ```

4. **Continue with setup as normal**

### Option 2: Install Visual C++ Build Tools

If you must use Python 3.13:

1. **Download and install Microsoft C++ Build Tools:**
   - https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - During installation, select "C++ build tools" workload

2. **Restart your terminal** after installation

3. **Try installing again:**
   ```bash
   pip install -r requirements.txt
   ```

### Option 3: Use Embedded ChromaDB (Alternative)

If you can't install build tools, you can try using ChromaDB's embedded mode without the HNSW index (slower but works):

1. **Install without chromadb:**
   ```bash
   pip install fastapi uvicorn python-multipart python-dotenv httpx pydantic PyPDF2 openai tiktoken
   ```

2. **Modify `vector_store.py`** to use a simpler vector store or wait for Python 3.13 wheels

## Recommended: Use Python 3.11

For the easiest setup, use Python 3.11. It's fully compatible with all dependencies and has pre-built wheels for Windows.
