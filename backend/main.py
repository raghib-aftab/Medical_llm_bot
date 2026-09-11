from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.chat import router as chat_router
from routes.auth import router as auth_router
from routes.appointments import router as appointments_router
from routes.profile import router as profile_router
from routes.hospitals import router as hospitals_router
from services.db_service import db_service
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    await db_service.connect()
    print("Connected to MongoDB")
    yield
    # Shutdown
    await db_service.close()
    print("Closed MongoDB connection")

app = FastAPI(title="Medical Healthcare API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://medical-ai-agent.netlify.app"],  # Vite and CRA default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(appointments_router)
app.include_router(profile_router)
app.include_router(hospitals_router)

@app.get("/")
async def root():
    return {"message": "Medical Healthcare API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
