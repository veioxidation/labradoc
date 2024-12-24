import uvicorn
from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import taxonomy, documents
# Import other routers as needed
from app.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    Base.metadata.create_all(bind=engine)

    # Register routers
    app.include_router(taxonomy.router)
    app.include_router(documents.router)
    # Add more routers (extraction, validation, metrics)...

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
