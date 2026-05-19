from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, workers, chat, bookings, ratings, notifications, requests, conversations, disputes, service_progress

app = FastAPI(title="Karoo API - Google Gemini Powered", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(workers.router, prefix="/api/workers", tags=["Workers"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(requests.router, prefix="/api/requests", tags=["Requests"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(disputes.router, prefix="/api/disputes", tags=["Disputes"])
app.include_router(service_progress.router, prefix="/api/service-progress", tags=["Service Progress"])

@app.get("/")
async def root():
    return {
        "status": "Karoo API running",
        "version": "2.0.0",
        "ai_engine": "Google Gemini 1.5 Flash",
        "features": [
            "Dynamic Pricing",
            "Scheduling Intelligence",
            "Dispute Resolution",
            "Service Quality Tracking",
            "Job Complexity Classification"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "ai_engine": "Google Gemini 1.5 Flash"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
