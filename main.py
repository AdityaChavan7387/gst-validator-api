import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.gstin import router as gstin_router
from app.routes.pan import router as pan_router
from app.routes.tan import router as tan_router
from app.routes.bulk import router as bulk_router
from app.routes.state import router as state_router

load_dotenv()

# ─── App Init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="India GST & Business Validator API",
    description="""
## India GST & Business Validator API

Validate Indian GSTIN numbers, extract PAN from GSTIN, check GSTIN format and checksum,
verify PAN and TAN formats, identify Indian state codes, and perform bulk GSTIN validation.

### Key Features
- GSTIN format and checksum validation
- Business registration details lookup
- GST return filing status
- PAN extraction from GSTIN
- PAN format validation with taxpayer type detection
- TAN format validation
- Bulk GSTIN validation up to 50 per call
- Vendor risk scoring

### Authentication
Pass your RapidAPI key in the X-RapidAPI-Key header.

### Disclaimer
This API provides validation support for business verification workflows only.
Not legal, tax, or compliance advice.
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "https://rapidapi.com",
    },
    license_info={
        "name": "Commercial — See RapidAPI Listing",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── RapidAPI Proxy Secret Verification ───────────────────────────────────────
RAPIDAPI_PROXY_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

OPEN_PATHS = {"/", "/docs", "/redoc", "/openapi.json", "/health"}

@app.middleware("http")
async def verify_rapidapi_proxy(request: Request, call_next):
    if ENVIRONMENT == "production" and RAPIDAPI_PROXY_SECRET:
        if request.url.path not in OPEN_PATHS:
            proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
            if proxy_secret != RAPIDAPI_PROXY_SECRET:
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error_code": "UNAUTHORIZED",
                        "message": "Access denied. This API must be accessed through RapidAPI.",
                    },
                )
    response = await call_next(request)
    return response


# ─── Request Timing Middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time)
    return response


# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(gstin_router)
app.include_router(pan_router)
app.include_router(tan_router)
app.include_router(bulk_router)
app.include_router(state_router)


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "India GST & Business Validator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": [
    "GET  /validate/{gstin}",
    "GET  /extract-pan/{gstin}",
    "GET  /gstin/info/{gstin}",
    "GET  /business/{gstin}",
    "GET  /business/{gstin}/returns",
    "GET  /pan/validate/{pan}",
    "GET  /tan/validate/{tan}",
    "POST /bulk-validate",
    "GET  /risk/{gstin}",
    "GET  /state/{state_code}",
    "GET  /states",
],
    }


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "healthy", "timestamp": time.time()}