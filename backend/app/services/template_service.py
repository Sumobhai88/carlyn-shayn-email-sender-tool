"""
Template business logic service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.models.template import Template


class TemplateService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_templates(self, skip: int = 0, limit: int = 100, user_id: int = None):
        """Get templates filtered by user"""
        query = self.db.query(Template)
        if user_id is not None:
            query = query.filter(Template.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    
    async def get_template(self, template_id: int, user_id: int = None):
        """Get template by ID"""
        query = self.db.query(Template).filter(Template.id == template_id)
        if user_id is not None:
            query = query.filter(Template.user_id == user_id)
        return query.first()
    
    async def create_template(self, template_data: dict) -> Template:
        """Create new template"""
        template = Template(**template_data)
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    async def update_template(self, template_id: int, template_data: dict, user_id: int = None) -> Template:
        """Update template"""
        template = await self.get_template(template_id, user_id=user_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        for field, value in template_data.items():
            if field != 'user_id':
                setattr(template, field, value)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    async def delete_template(self, template_id: int, user_id: int = None):
        """Delete template"""
        template = await self.get_template(template_id, user_id=user_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        self.db.delete(template)
        self.db.commit()
