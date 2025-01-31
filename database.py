from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models.DataModels import Base

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL,
                       echo=False,
                       connect_args={"options":f"-csearch_path={settings.SCHEMA_NAME}"})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)


# Create all tables in the database
def create_all():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




if __name__ == "__main__":
    create_all()