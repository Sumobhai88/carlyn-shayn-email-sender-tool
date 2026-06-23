"""
Template endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("/")
async def get_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all templates"""
    service = TemplateService(db)
    templates = await service.get_templates(skip=skip, limit=limit)
    return templates


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get template by ID"""
    service = TemplateService(db)
    return await service.get_template(template_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: dict,
    db: Session = Depends(get_db)
):
    """Create new template"""
    service = TemplateService(db)
    template = await service.create_template(template_data)
    return template


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    template_data: dict,
    db: Session = Depends(get_db)
):
    """Update template"""
    service = TemplateService(db)
    return await service.update_template(template_id, template_data)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete template"""
    service = TemplateService(db)
    await service.delete_template(template_id)
    return None
