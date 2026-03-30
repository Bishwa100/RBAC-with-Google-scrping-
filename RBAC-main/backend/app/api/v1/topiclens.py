"""
TopicLens API Routes
Protected endpoints for content analysis and web scraping
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.session import get_db
from app.core.deps import get_current_user, RequireScope
from app.models.all import User
from app.schemas.common import success_response, error_response
from pydantic import BaseModel, Field

# Import TopicLens modules
from app.topiclens.config import topiclens_settings
from app.topiclens.models import SearchRequest, SearchResponse, JobStatus, AnalyzeRequest

router = APIRouter()

# ============================================================================
# TopicLens Schemas
# ============================================================================

class TopicSearchRequest(BaseModel):
    """Request schema for topic search"""
    topic: str = Field(..., min_length=1, max_length=200, description="Topic or keyword to search")
    sources: List[str] = Field(..., min_items=1, description="List of sources to scrape")
    deep_analysis: bool = Field(False, description="Enable deep LLM analysis")

class ContentAnalyzeRequest(BaseModel):
    """Request schema for content analysis"""
    url: str = Field(..., description="URL to analyze")

# ============================================================================
# Protected TopicLens Endpoints (Root User Only)
# ============================================================================

@router.post("/search", response_model=dict)
async def search_topic(
    data: TopicSearchRequest,
    current_user: User = Depends(RequireScope("topiclens", "access")),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new topic search job
    
    **Permissions Required:** topiclens:access (Root user only)
    
    - **topic**: The topic or keyword to search for
    - **sources**: List of sources to scrape (e.g., github, reddit, youtube)
    - **deep_analysis**: Enable AI-powered deep analysis
    """
    try:
        # Import here to avoid circular dependency
        from app.topiclens.tasks import scrape_topic_task
        
        # Validate sources
        invalid_sources = [s for s in data.sources if s not in topiclens_settings.available_sources]
        if invalid_sources:
            return error_response(
                error="invalid_sources",
                detail=f"Invalid sources: {', '.join(invalid_sources)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Create job in database
        from app.topiclens.database import create_job
        job_id = await create_job(
            db=db,
            topic=data.topic,
            sources=data.sources,
            deep_analysis=data.deep_analysis,
            user_id=current_user.id
        )
        
        # Queue the task
        task = scrape_topic_task.delay(
            job_id=job_id,
            topic=data.topic,
            sources=data.sources,
            deep_analysis=data.deep_analysis
        )
        
        return success_response(
            data={
                "job_id": job_id,
                "task_id": task.id,
                "message": "Search job started successfully"
            }
        )
        
    except Exception as e:
        return error_response(
            error="search_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/status/{job_id}", response_model=dict)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(RequireScope("topiclens", "access")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a search job
    
    **Permissions Required:** topiclens:access (Root user only)
    """
    try:
        from app.topiclens.database import get_job
        
        job = await get_job(db, job_id)
        
        if not job:
            return error_response(
                error="job_not_found",
                detail=f"Job {job_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user owns this job
        if job.user_id != current_user.id and not current_user.email == "root@system.local":
            return error_response(
                error="forbidden",
                detail="You don't have permission to view this job",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return success_response(data=job.to_dict())
        
    except Exception as e:
        return error_response(
            error="status_check_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/analyze", response_model=dict)
async def analyze_content(
    data: ContentAnalyzeRequest,
    current_user: User = Depends(RequireScope("topiclens", "access")),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze content from a URL
    
    **Permissions Required:** topiclens:access (Root user only)
    """
    try:
        from app.topiclens.analyzers.content_analysis import analyze_url
        
        # Create analysis job
        from app.topiclens.database import create_job
        job_id = await create_job(
            db=db,
            topic=f"Analysis: {data.url}",
            sources=["url"],
            deep_analysis=True,
            user_id=current_user.id
        )
        
        # Queue analysis task
        result = await analyze_url(data.url)
        
        # Update job with result
        from app.topiclens.database import update_job_status
        await update_job_status(
            db=db,
            job_id=job_id,
            status="completed",
            result=result
        )
        
        return success_response(
            data={
                "job_id": job_id,
                "result": result,
                "message": "Content analyzed successfully"
            }
        )
        
    except Exception as e:
        return error_response(
            error="analysis_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/sources", response_model=dict)
async def get_available_sources(
    current_user: User = Depends(RequireScope("topiclens", "access"))
):
    """
    Get list of available sources for scraping
    
    **Permissions Required:** topiclens:access (Root user only)
    """
    return success_response(
        data={
            "sources": topiclens_settings.available_sources
        }
    )


@router.get("/jobs", response_model=dict)
async def get_all_jobs(
    current_user: User = Depends(RequireScope("topiclens", "access")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Get all jobs for current user (or all jobs if root)
    
    **Permissions Required:** topiclens:access (Root user only)
    """
    try:
        from app.topiclens.database import get_user_jobs
        
        # Root user sees all jobs, others see only their own
        user_id = None if current_user.email == "root@system.local" else current_user.id
        
        jobs = await get_user_jobs(db, user_id=user_id, limit=limit, offset=offset)
        
        return success_response(
            data={
                "jobs": [job.to_dict() for job in jobs],
                "count": len(jobs)
            }
        )
        
    except Exception as e:
        return error_response(
            error="jobs_fetch_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/health", response_model=dict)
async def topiclens_health():
    """
    Health check for TopicLens module
    
    **Public endpoint** - No authentication required
    """
    return success_response(
        data={
            "status": "healthy",
            "module": "topiclens",
            "available_sources": len(topiclens_settings.available_sources)
        }
    )
