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
    
    async def get_templates(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Template]:
        """Get all templates"""
        return self.db.query(Template).offset(skip).limit(limit).all()
    
    async def get_template(self, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        return self.db.query(Template).filter(
            Template.id == template_id
        ).first()
    
    async def create_template(self, template_data: dict) -> Template:
        """Create new template"""
        template = Template(**template_data)
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    async def update_template(
        self, 
        template_id: int, 
        template_data: dict
    ) -> Template:
        """Update template"""
        template = await self.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        for field, value in template_data.items():
            setattr(template, field, value)
        
        self.db.commit()
        self.db.refresh(template)
        return template
    
    async def delete_template(self, template_id: int):
        """Delete template"""
        template = await self.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        self.db.delete(template)
        self.db.commit()
