from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables
from routes import books, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Database tables created.")
    yield
    print("Application shutdown")


app = FastAPI(
    title="BookLoop API",
    description="""
## 📚 BookLoop API

A simple REST API for exchanging used books.

### Features

- 👤 User registration and authentication
- 📖 Add and manage books
- 🔍 Search and filter books
- 💰 Mark books as sold
- 🔐 API key authentication

### Authentication

Some endpoints require an API key.
Pass the API key using the `X-API-Key` header.
""",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(books.router)


@app.get("/", tags=["Health"])
def home():
    return {
        "message": "Welcome to the Kitab Exchange API",
        "version": "1.0.0",
        "status": "running",
    }
