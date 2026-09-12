from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from brain.api.routes import router

app = FastAPI(title="Digital Twin — Brain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "brain online"}