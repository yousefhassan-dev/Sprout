"""
Sprout API
A gamified habit tracker: log activities, grow a pixel-art garden,
generate shareable weekly recap cards.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sprout API", version="0.1.0")

# Allow the frontend (running on a different port/domain) to call this API.
# In production, replace "*" with your actual deployed frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Simple endpoint to confirm the API is alive. Useful for deployment checks."""
    return {"status": "ok"}
