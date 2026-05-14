"""FastAPI Workshop — Starter App.

This is your starting point. It only has a health check.
Your job: build the Ideas API phase by phase using Copilot.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Ideas API",
    description="API for managing startup ideas",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
