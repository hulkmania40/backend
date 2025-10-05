from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from routes import invoice, user, item

app = FastAPI()

# ✅ Add CORS Middleware
origins = [
    "http://localhost:5173",   # React local dev
    "http://127.0.0.1:3000",
    "http://192.168.0.104:5173/",
    "http://localhost:8000/",
    # "https://your-frontend-domain.com"  # Deployed frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # or ["*"] for all origins (not safe for prod)
    allow_credentials=True,
    allow_methods=["*"],          # ["GET", "POST", ...]
    allow_headers=["*"],          # ["Content-Type", "Authorization", ...]
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Routes
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(item.router, prefix="/items", tags=["Items"])
app.include_router(invoice.router, prefix="/invoices", tags=["Invoices"])

@app.get("/")
def root():
    return {"message": "API running 🚀"}

# uvicorn main:app --reload