"""
FastAPI main application for zjia_job backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.resume import router as resume_router
from app.api.job_matching import router as job_matching_router

app = FastAPI(
    title="ZJia Job API",
    description="Job scraping and resume parsing platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api/v1")
app.include_router(job_matching_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "ZJia Job API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
