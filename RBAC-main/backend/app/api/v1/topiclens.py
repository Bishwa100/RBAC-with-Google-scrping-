"""
TopicLens API Routes
Protected endpoints for content analysis and web scraping
"""
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
import uuid
from app.db.session import get_db
from app.core.deps import get_current_user, RequireScope, RequireRootUser, is_root_user
from app.models.all import User, Role
from app.models.topiclens import TopicLensSharedContent, TopicLensResult, TopicLensJob
from app.schemas.common import success_response, error_response
from app.schemas.topiclens_sharing import (
    ShareContentRequest, 
    ShareContentResponse, 
    SharedContentItem,
    MySharedContentResponse,
    AllSharedContentResponse
)
from pydantic import BaseModel, Field
from datetime import datetime

# Import TopicLens modules
from app.topiclens.config import topiclens_settings

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
    current_user: User = Depends(RequireRootUser()),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new topic search job.
    
    **Root/Admin only** - Only root users can search topics
    
    - **topic**: The topic or keyword to search for
    - **sources**: List of sources to scrape (e.g., github, reddit, youtube)
    - **deep_analysis**: Enable AI-powered deep analysis
    """
    try:
        # Validate sources
        invalid_sources = [s for s in data.sources if s not in topiclens_settings.available_sources]
        if invalid_sources:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response(
                    error="invalid_sources",
                    detail=f"Invalid sources: {', '.join(invalid_sources)}"
                )
            )
        
        # Create job in database using SQLAlchemy model
        job_id = str(uuid.uuid4())
        new_job = TopicLensJob(
            id=job_id,
            user_id=current_user.id,
            topic=data.topic,
            sources=data.sources,
            deep_analysis=data.deep_analysis,
            status="pending"
        )
        db.add(new_job)
        await db.commit()
        
        # Queue the background task
        try:
            from app.topiclens.tasks import scrape_topic_task
            task = scrape_topic_task.delay(
                job_id=job_id,
                topic=data.topic,
                sources=data.sources,
                deep_analysis=data.deep_analysis
            )
            task_id = task.id
        except Exception as task_err:
            # If Celery is not available, run synchronously or mark as pending
            task_id = None
        
        return success_response(
            data={
                "job_id": job_id,
                "task_id": task_id,
                "message": "Search job started successfully"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                error="search_failed",
                detail=str(e)
            )
        )


@router.get("/status/{job_id}", response_model=dict)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a search job.
    """
    try:
        # Query job from database
        result = await db.execute(
            select(TopicLensJob).where(TopicLensJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response(
                    error="job_not_found",
                    detail=f"Job {job_id} not found"
                )
            )
        
        # Check if user owns this job or is root
        is_root = any(
            ur.role.name.lower() in ['root', 'admin'] or ur.role.level == 0
            for ur in current_user.roles
        )
        if str(job.user_id) != str(current_user.id) and not is_root:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=error_response(
                    error="forbidden",
                    detail="You don't have permission to view this job"
                )
            )
        
        return success_response(data=job.to_dict())
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                error="status_check_failed",
                detail=str(e)
            )
        )


@router.post("/analyze", response_model=dict)
async def analyze_content(
    data: ContentAnalyzeRequest,
    current_user: User = Depends(RequireRootUser()),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze content from a URL.
    
    **Root/Admin only**
    """
    try:
        # Create analysis job
        job_id = str(uuid.uuid4())
        new_job = TopicLensJob(
            id=job_id,
            user_id=current_user.id,
            topic=f"Analysis: {data.url}",
            sources=["url"],
            deep_analysis=True,
            status="pending"
        )
        db.add(new_job)
        await db.commit()
        
        # For now, return the job ID - actual analysis can be async
        return success_response(
            data={
                "job_id": job_id,
                "message": "Analysis job created"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                error="analysis_failed",
                detail=str(e)
            )
        )


@router.get("/sources", response_model=dict)
async def get_available_sources(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available sources for scraping.
    """
    return success_response(
        data={
            "sources": topiclens_settings.available_sources
        }
    )


@router.get("/jobs", response_model=dict)
async def get_all_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Get all jobs for current user (or all jobs if root).
    """
    try:
        # Check if user is root
        is_root = any(
            ur.role.name.lower() in ['root', 'admin'] or ur.role.level == 0
            for ur in current_user.roles
        )
        
        # Build query
        if is_root:
            query = select(TopicLensJob).order_by(TopicLensJob.created_at.desc())
        else:
            query = select(TopicLensJob).where(
                TopicLensJob.user_id == current_user.id
            ).order_by(TopicLensJob.created_at.desc())
        
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return success_response(
            data={
                "jobs": [job.to_dict() for job in jobs],
                "count": len(jobs)
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                error="jobs_fetch_failed",
                detail=str(e)
            )
        )


@router.get("/jobs/{job_id}", response_model=dict)
async def get_job_by_id(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific job by ID.
    """
    try:
        result = await db.execute(
            select(TopicLensJob).where(TopicLensJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response(
                    error="job_not_found",
                    detail=f"Job {job_id} not found"
                )
            )
        
        # Check if user owns this job or is root
        is_root = any(
            ur.role.name.lower() in ['root', 'admin'] or ur.role.level == 0
            for ur in current_user.roles
        )
        if str(job.user_id) != str(current_user.id) and not is_root:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=error_response(
                    error="forbidden",
                    detail="You don't have permission to view this job"
                )
            )
        
        return success_response(data=job.to_dict())
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                error="job_fetch_failed",
                detail=str(e)
            )
        )


@router.get("/health", response_model=dict)
async def topiclens_health():
    """
    Health check for TopicLens module.
    
    **Public endpoint** - No authentication required
    """
    return success_response(
        data={
            "status": "healthy",
            "module": "topiclens",
            "available_sources": len(topiclens_settings.available_sources)
        }
    )


# ============================================================================
# Content Sharing Endpoints
# ============================================================================

@router.post("/share", response_model=dict)
async def share_content(
    data: ShareContentRequest,
    current_user: User = Depends(RequireRootUser()),
    db: AsyncSession = Depends(get_db)
):
    """
    Share TopicLens content with specific roles.
    
    **Root/Admin only** - Only root users can share content
    
    - **result_id**: ID of the TopicLens result to share
    - **job_id**: ID of the TopicLens job
    - **role_ids**: List of role IDs to share with
    - **notes**: Optional notes for the shared content
    """
    try:
        # Verify result exists
        result_query = await db.execute(
            select(TopicLensResult).where(TopicLensResult.id == data.result_id)
        )
        result = result_query.scalar_one_or_none()
        
        if not result:
            return error_response(
                error="result_not_found",
                detail=f"Result {data.result_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Verify job exists
        job_query = await db.execute(
            select(TopicLensJob).where(TopicLensJob.id == data.job_id)
        )
        job = job_query.scalar_one_or_none()
        
        if not job:
            return error_response(
                error="job_not_found",
                detail=f"Job {data.job_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Verify all roles exist
        roles_query = await db.execute(
            select(Role).where(Role.id.in_(data.role_ids))
        )
        roles = roles_query.scalars().all()
        
        if len(roles) != len(data.role_ids):
            return error_response(
                error="invalid_roles",
                detail="One or more role IDs are invalid",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Create share records
        share_ids = []
        for role_id in data.role_ids:
            # Check if already shared with this role
            existing_query = await db.execute(
                select(TopicLensSharedContent).where(
                    TopicLensSharedContent.result_id == data.result_id,
                    TopicLensSharedContent.shared_with_role_id == role_id
                )
            )
            existing = existing_query.scalar_one_or_none()
            
            if existing:
                share_ids.append(str(existing.id))
                continue
            
            # Create new share
            share = TopicLensSharedContent(
                result_id=data.result_id,
                job_id=data.job_id,
                shared_by_user_id=current_user.id,
                shared_with_role_id=role_id,
                notes=data.notes
            )
            db.add(share)
            await db.flush()
            share_ids.append(str(share.id))
        
        await db.commit()
        
        return success_response(
            data={
                "success": True,
                "message": f"Content shared with {len(data.role_ids)} role(s)",
                "shared_count": len(data.role_ids),
                "share_ids": share_ids
            }
        )
        
    except Exception as e:
        await db.rollback()
        return error_response(
            error="share_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/my-shared-content", response_model=dict)
async def get_my_shared_content(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Get content shared with the current user's roles.
    
    **Authenticated users** - Returns content shared with any of user's roles
    """
    try:
        # Get user's role IDs
        user_role_ids = [ur.role_id for ur in current_user.roles]
        
        if not user_role_ids:
            return success_response(
                data={
                    "items": [],
                    "total": 0
                }
            )
        
        # Query shared content
        query = (
            select(TopicLensSharedContent)
            .options(
                selectinload(TopicLensSharedContent.result),
                selectinload(TopicLensSharedContent.job),
                selectinload(TopicLensSharedContent.shared_by),
                selectinload(TopicLensSharedContent.shared_with_role)
            )
            .where(TopicLensSharedContent.shared_with_role_id.in_(user_role_ids))
            .order_by(TopicLensSharedContent.shared_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(query)
        shared_items = result.scalars().all()
        
        # Build response items
        items = []
        for share in shared_items:
            items.append({
                "share_id": str(share.id),
                "result_id": share.result_id,
                "job_id": share.job_id,
                "topic": share.job.topic,
                "source": share.result.source,
                "url": share.result.url,
                "title": share.result.title,
                "content": share.result.content,
                "metadata": share.result.result_metadata,
                "sentiment": share.result.sentiment,
                "keywords": share.result.keywords,
                "summary": share.result.summary,
                "shared_by_user_id": str(share.shared_by_user_id),
                "shared_by_username": share.shared_by.username,
                "shared_with_role_id": str(share.shared_with_role_id),
                "shared_with_role_name": share.shared_with_role.name,
                "notes": share.notes,
                "shared_at": share.shared_at.isoformat(),
                "created_at": share.result.created_at.isoformat()
            })
        
        return success_response(
            data={
                "items": items,
                "total": len(items)
            }
        )
        
    except Exception as e:
        return error_response(
            error="fetch_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/shared", response_model=dict)
async def get_all_shared_content(
    current_user: User = Depends(RequireRootUser()),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    role_id: Optional[str] = None
):
    """
    Get all shared content across the system.
    
    **Root/Admin only** - View all shared content with optional role filter
    """
    try:
        # Build query
        query = (
            select(TopicLensSharedContent)
            .options(
                selectinload(TopicLensSharedContent.result),
                selectinload(TopicLensSharedContent.job),
                selectinload(TopicLensSharedContent.shared_by),
                selectinload(TopicLensSharedContent.shared_with_role)
            )
            .order_by(TopicLensSharedContent.shared_at.desc())
        )
        
        # Apply role filter if provided
        if role_id:
            query = query.where(TopicLensSharedContent.shared_with_role_id == UUID(role_id))
        
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        shared_items = result.scalars().all()
        
        # Build response items
        items = []
        for share in shared_items:
            items.append({
                "share_id": str(share.id),
                "result_id": share.result_id,
                "job_id": share.job_id,
                "topic": share.job.topic,
                "source": share.result.source,
                "url": share.result.url,
                "title": share.result.title,
                "content": share.result.content,
                "metadata": share.result.result_metadata,
                "sentiment": share.result.sentiment,
                "keywords": share.result.keywords,
                "summary": share.result.summary,
                "shared_by_user_id": str(share.shared_by_user_id),
                "shared_by_username": share.shared_by.username,
                "shared_with_role_id": str(share.shared_with_role_id),
                "shared_with_role_name": share.shared_with_role.name,
                "notes": share.notes,
                "shared_at": share.shared_at.isoformat(),
                "created_at": share.result.created_at.isoformat()
            })
        
        return success_response(
            data={
                "items": items,
                "total": len(items)
            }
        )
        
    except Exception as e:
        return error_response(
            error="fetch_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/share/{share_id}", response_model=dict)
async def revoke_share(
    share_id: str,
    current_user: User = Depends(RequireRootUser()),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke shared access to content.
    
    **Root/Admin only** - Remove content sharing
    """
    try:
        # Find the share
        query = await db.execute(
            select(TopicLensSharedContent).where(TopicLensSharedContent.id == UUID(share_id))
        )
        share = query.scalar_one_or_none()
        
        if not share:
            return error_response(
                error="share_not_found",
                detail=f"Share {share_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Delete the share
        await db.delete(share)
        await db.commit()
        
        return success_response(
            data={
                "success": True,
                "message": "Share revoked successfully"
            }
        )
        
    except Exception as e:
        await db.rollback()
        return error_response(
            error="revoke_failed",
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
