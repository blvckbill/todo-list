import logging
from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.blogs.router import router as blogs_router

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)  # This will log all messages at DEBUG level and above

app = FastAPI(title="AI Powered Blog Post Generator")

# Include routers
app.include_router(auth_router)
app.include_router(blogs_router)

@app.get("/")
def root():
    return {"message": "Welcome to the AI Blog Post Generator"}

@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    logging.error(f"Error occurred: {exc}")
    return {"message": "Internal Server Error", "details": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)