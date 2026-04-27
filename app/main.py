from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import Base, engine
from app.models import user, account, transaction  # ensures models are registered
from app.router import user as user_router
from app.router import account as account_router
from app.router import transaction as transaction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: nothing needed for SQLite


app = FastAPI(
    title="Expense Tracker API",
    description="A production-ready expense tracker with auth, accounts, and transactions.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allows frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user_router.router)
app.include_router(account_router.router)
app.include_router(transaction_router.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Expense Tracker API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
