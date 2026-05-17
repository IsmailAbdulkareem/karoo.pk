from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, workers, chat, bookings, ratings, notifications, requests

app = FastAPI(title="Karoo API", version="1.0.0")

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

@app.get("/")
async def root():
    return {"status": "Karoo API running", "version": "1.0.0"}
