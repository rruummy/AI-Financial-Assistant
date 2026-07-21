from fastapi import FastAPI

from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router
from app.api.category_router import router as category_router
from app.api.transaction_router import router as transaction_router
from app.api.ai_router import router as ai_router


app = FastAPI(
    title="AI Financial Assistant",
    version="1.0.0",
    description="AI-powered personal finance assistant",
)


@app.get("/")
def root():
    return {
        "message": "AI Financial Assistant API"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(transaction_router)
app.include_router(ai_router)