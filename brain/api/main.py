from fastapi import FastAPI
from brain.api.routes import router

app = FastAPI(title="Digital Twin — Brain")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "brain online"}
