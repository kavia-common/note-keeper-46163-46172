from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .repository import get_repository

openapi_tags = [
    {
        "name": "health",
        "description": "Service health and meta endpoints",
    },
    {
        "name": "notes",
        "description": "Operations for managing notes",
    },
]

app = FastAPI(
    title="Notes Backend API",
    description="API for managing notes with CRUD and search.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Initialize singleton repository (for future endpoint use)
repo = get_repository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Health check endpoint for the Notes API.

    Returns:
        A JSON object indicating service health.
    """
    return {"message": "Healthy"}
