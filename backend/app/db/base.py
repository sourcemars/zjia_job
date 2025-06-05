from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def create_tables():
    """Create all database tables."""
    import app.models
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
