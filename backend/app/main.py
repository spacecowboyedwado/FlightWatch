from fastapi import FastAPI
from backend.app.controllers.image_route import router as image_route
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:3000",  # Default for Create React App
    "http://localhost:5173",  # Default for Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_route)

@app.get("/")
async def root():
    return {"message": "Welcome to Flight Watch. Go to /docs to test file uploads!"}