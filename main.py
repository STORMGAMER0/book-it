import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router.auth import auth_router
from api.router.booking import booking_router
from api.router.service import service_router
from api.router.user import user_router
from api.router.review import review_router


app = FastAPI(title="BookIt API",
    description="A simple bookings platform API",
    version="1.0.0")

if os.getenv("DEBUG") == "False":
    app.docs_url = "/docs"  # Keep docs available
    app.redoc_url = "/redoc"

app.add_middleware(
    CORSMiddleware,
allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(service_router)
app.include_router(booking_router)
app.include_router(review_router)

@app.get("/")
async def root():
    return {"message": "BookIt API is running!"}
