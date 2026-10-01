# Panduan & Desain Arsitektur: Migrasi ke FastAPI + Uvicorn

Dokumen ini memuat analisis arsitektur, desain sistem, dan blueprint implementasi untuk memigrasikan backend **SCRAPE_TKA** dari Python standard library (`ThreadingHTTPServer`) ke **FastAPI + Uvicorn**.

---

## 1. Latar Belakang & Motivasi

Saat ini, backend menggunakan `ThreadingHTTPServer` dari library bawaan Python (`server.py`).

| Aspek | `ThreadingHTTPServer` (Saat Ini) | `FastAPI + Uvicorn` (Target Migrasi) |
| :--- | :--- | :--- |
| **Model Konkurensi** | Multi-threaded (1 thread OS per request). Pada Windows, overhead pembuatan thread tinggi dan rawan bottleneck jika 50 siswa aktif bersamaan. | Asynchronous Event Loop (`asyncio`) berbasis `uvicorn` (ASGI). Mampu melayani ribuan request konkuren secara non-blocking. |
| **Validasi Payload** | Manual via `json.loads(post_data)` dan `dict.get()`. Rawan bug `KeyError` atau tipe data salah. | Otomatis divalidasi oleh **Pydantic**. Parameter tidak valid otomatis menghasilkan error HTTP 422 dengan pesan detail. |
| **Keamanan File Statis** | Custom override `SimpleHTTPRequestHandler` dengan filter manual di `do_GET`. | `StaticFiles` bawaan Starlette dengan proteksi path traversal out-of-the-box dan whitelist direktori publik. |
| **Dokumentasi API** | Tidak ada. | Otomatis dibuatkan **Swagger UI** interaktif di `/docs` dan **ReDoc** di `/redoc`. |
| **Testing** | Menjalankan server di thread terpisah (`ThreadingHTTPServer`) dan memanggil via socket `urllib`. | Cukup menggunakan `httpx.AsyncClient` atau `TestClient` bawaan tanpa perlu membuka port sistem nyata. |

---

## 2. Struktur Desain API (Pydantic Models & Endpoints)

### A. Skema Data (Pydantic Models)

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

class TutorChatRequest(BaseModel):
    subject: str = Field(default="matematika", description="Slug mata pelajaran")
    paket: int = Field(default=1, ge=1, le=2, description="Nomor paket soal (1 atau 2)")
    nomor: int = Field(ge=1, description="Nomor soal aktif")
    message: str = Field(min_length=1, max_length=2000, description="Pesan pertanyaan siswa")
    request_id: Optional[str] = Field(default=None, description="Idempotency key per pesan")

class TutorChatResponse(BaseModel):
    status: str
    reply: str
    conversation_id: int
    message_id: int
    intent: str

class TutorStateResponse(BaseModel):
    status: str
    canonical_id: str
    provider: Dict[str, Any]
    conversation_id: Optional[int]
    summary: Optional[str]
    messages: List[Dict[str, Any]]

class SolutionRequest(BaseModel):
    subject: str = "matematika"
    paket: int = 1
    nomor: int = 1
```

---

## 3. Blueprint Implementasi (`server_fastapi.py`)

```python
# -*- coding: utf-8 -*-
"""server_fastapi.py — REST API & Static Server modern berbasis FastAPI."""
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import solution_loader
import tutor_engine
import tutor_llm
import tutor_store

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inisialisasi database SQLite saat startup
    tutor_store.init_db()
    yield

app = FastAPI(
    title="CBT TKA Master API",
    description="Backend API untuk Simulasi CBT dan AI Tutor Interaktif",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Sesi Anonim Helper
# ---------------------------------------------------------------------------
def get_user_session(request: Request, response: Response) -> str:
    cookie_val = request.cookies.get("tutor_uid")
    user_key = tutor_store.validate_user_cookie_value(cookie_val) if cookie_val else None
    if not user_key:
        new_val = tutor_store.make_user_cookie_value()
        user_key = new_val.split(".", 1)[0]
        response.set_cookie(
            key="tutor_uid",
            value=new_val,
            max_age=31536000,
            httponly=True,
            samesite="lax",
            path="/"
        )
    return user_key

# ---------------------------------------------------------------------------
# Endpoints AI Tutor & Solution
# ---------------------------------------------------------------------------
@app.get("/api/tutor/state", response_model=TutorStateResponse)
async def get_tutor_state(
    subject: str = "matematika",
    paket: int = 1,
    nomor: int = 1,
    request: Request = None,
    response: Response = None
):
    user_key = get_user_session(request, response)
    # Gunakan logika penyusunan konteks yang sama
    ...

@app.post("/api/tutor/chat", response_model=TutorChatResponse)
async def post_tutor_chat(
    payload: TutorChatRequest,
    request: Request,
    response: Response
):
    user_key = get_user_session(request, response)
    # Integrasi concurrency semaphore & LLM streaming/generate
    ...

@app.post("/api/solution")
async def post_solution(payload: SolutionRequest):
    # Handler pembahasan Layer 3
    ...

# ---------------------------------------------------------------------------
# Static Files Serving (Aman & Terisolasi)
# ---------------------------------------------------------------------------
# Mount hanya aset publik
app.mount("/data", StaticFiles(directory=os.path.join(BASE_DIR, "data")), name="data")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/{file_name}")
async def serve_root_files(file_name: str):
    allowed_files = {"app.js", "style.css", "favicon.ico"}
    if file_name in allowed_files:
        return FileResponse(os.path.join(BASE_DIR, file_name))
    raise HTTPException(status_code=404, detail="File not found")
```

---

## 4. Langkah Migrasi & Dependensi

1. **Instalasi Paket Dependensi:**
   ```bash
   pip install fastapi uvicorn[standard] pydantic
   ```
2. **Uji Kompatibilitas Frontend:**
   Karena URL endpoint dan format JSON respon dibuat sama persis dengan `server.py`, file [`app.js`](file:///d:/PROJECTS/SCRAPE_TKA/app.js) tidak memerlukan perubahan apa pun.
3. **Pembaruan Launcher [`start_server.bat`](file:///d:/PROJECTS/SCRAPE_TKA/start_server.bat):**
   ```bat
   uvicorn server_fastapi:app --host 0.0.0.0 --port 8080 --reload
   ```
