from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

# Use PostgreSQL from environment, with SQLite fallback for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./topicLens.db")

# Convert asyncpg URL to sync psycopg2 for Celery tasks
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# For SQLite, add check_same_thread
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SearchJob(Base):
    """Legacy search_jobs table - kept for backward compatibility"""
    __tablename__ = "search_jobs"

    id = Column(String, primary_key=True, index=True)
    topic = Column(String, index=True)
    status = Column(String, default="pending")
    results = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_results(job_id: str, topic: str, data: dict):
    """Save results to database"""
    db = SessionLocal()
    try:
        # Try to update topiclens_jobs table (new schema)
        from sqlalchemy import text
        
        # Update the main topiclens_jobs table
        db.execute(
            text("""
                UPDATE topiclens_jobs 
                SET status = :status, 
                    progress = :progress,
                    result = :result,
                    completed_at = :completed_at
                WHERE id = :job_id
            """),
            {
                "status": "completed",
                "progress": 100,
                "result": json.dumps(data),
                "completed_at": datetime.utcnow(),
                "job_id": job_id
            }
        )
        db.commit()
        print(f"[Database] Successfully saved results for job {job_id}")
    except Exception as e:
        print(f"[Database Error] Failed to save results: {e}")
        db.rollback()
    finally:
        db.close()


def get_job(job_id: str) -> dict | None:
    db = SessionLocal()
    try:
        from sqlalchemy import text
        result = db.execute(
            text("SELECT id, topic, status, result, progress, created_at, completed_at FROM topiclens_jobs WHERE id = :job_id"),
            {"job_id": job_id}
        ).fetchone()
        
        if result:
            return {
                "id": result[0],
                "topic": result[1],
                "status": result[2],
                "results": json.loads(result[3]) if result[3] else None,
                "progress": result[4] or 0,
                "created_at": result[5].isoformat() if result[5] else None,
                "completed_at": result[6].isoformat() if result[6] else None
            }
        return None
    finally:
        db.close()


def create_job(job_id: str, topic: str):
    """Create job - note: this is now handled by the API using TopicLensJob model"""
    # This function is kept for backward compatibility but jobs are created via API
    pass


def update_job_status(job_id: str, status: str, step: str = None, progress: int = None, results: dict = None):
    """Update job status with progress information in the PostgreSQL database."""
    db = SessionLocal()
    try:
        from sqlalchemy import text
        
        # Build update query dynamically
        update_fields = ["status = :status"]
        params = {"status": status, "job_id": job_id}
        
        if progress is not None:
            update_fields.append("progress = :progress")
            params["progress"] = progress
        
        if results is not None:
            update_fields.append("result = :result")
            params["result"] = json.dumps(results)
        
        if status in ["done", "completed"]:
            update_fields.append("completed_at = :completed_at")
            params["completed_at"] = datetime.utcnow()
        elif status == "failed":
            update_fields.append("error_message = :error_message")
            params["error_message"] = step or "Unknown error"
        
        query = f"UPDATE topiclens_jobs SET {', '.join(update_fields)} WHERE id = :job_id"
        db.execute(text(query), params)
        db.commit()
        print(f"[Database] Updated job {job_id}: status={status}, progress={progress}")
    except Exception as e:
        print(f"[Database Error] Failed to update job status: {e}")
        db.rollback()
    finally:
        db.close()
