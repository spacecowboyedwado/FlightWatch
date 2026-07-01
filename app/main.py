from fastapi import FastAPI
from main.controllers.image_route import router as image_route

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Flight Watch. Go to /docs to test file uploads!"}