"""
Main API router combining all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    smtp_profiles,
    campaigns,
    recipients,
    templates,
    analytics,
    exports,
    progress,
    tracking,
    unsubscribe,
    bounces,
    settings,
    admin
)

api_router = APIRouter()

# Auth routes (no prefix for cleaner URLs)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["Settings"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

# Include all routers
api_router.include_router(
    smtp_profiles.router,
    prefix="/smtp-profiles",
    tags=["SMTP Profiles"]
)

api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["Campaigns"]
)

api_router.include_router(
    recipients.router,
    prefix="/recipients",
    tags=["Recipients"]
)

api_router.include_router(
    templates.router,
    prefix="/templates",
    tags=["Templates"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    exports.router,
    prefix="/exports",
    tags=["Exports"]
)

api_router.include_router(
    progress.router,
    prefix="/progress",
    tags=["Progress Tracking"]
)

api_router.include_router(
    tracking.router,
    prefix="/tracking",
    tags=["Email Tracking"]
)

api_router.include_router(
    unsubscribe.router,
    prefix="/unsubscribe",
    tags=["Unsubscribe Management"]
)

api_router.include_router(
    bounces.router,
    prefix="/bounces",
    tags=["Bounce Handling"]
)
