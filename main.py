from fastapi import FastAPI

app = FastAPI(
    title="Project Name",
    description="Project description",
    version="0.2.0"
)

TEAM_NAME = "404"

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/version")
async def version():
    """Версия приложения и команда-владелец."""
    return {"version": app.version, "team": TEAM_NAME}