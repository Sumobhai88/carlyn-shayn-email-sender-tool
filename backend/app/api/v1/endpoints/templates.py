"""
Template endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("/")
async def get_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get templates for current user only"""
    service = TemplateService(db)
    templates = await service.get_templates(skip=skip, limit=limit, user_id=current_user.id)
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "subject": t.subject,
                "body": t.body,
                "category": t.category or "General",
                "usage_count": t.usage_count or 0,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in templates
        ],
        "total": len(templates)
    }


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get template by ID"""
    service = TemplateService(db)
    t = await service.get_template(template_id, user_id=current_user.id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new template for current user"""
    template_data['user_id'] = current_user.id
    service = TemplateService(db)
    t = await service.create_template(template_data)
    return {
        "id": t.id,
        "name": t.name,
        "subject": t.subject,
        "body": t.body,
        "category": t.category or "General",
        "usage_count": t.usage_count or 0,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    template_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update template - only if owned by current user"""
    service = TemplateService(db)
    t = await service.update_template(template_id, template_data, user_id=current_user.id)
    return {
        "id": t.id,
        "name": t.name,
        "subject": t.subject,
        "body": t.body,
        "category": t.category or "General",
        "usage_count": t.usage_count or 0,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete template - only if owned by current user"""
    service = TemplateService(db)
    await service.delete_template(template_id, user_id=current_user.id)
    return None
