"""
SMTP profile CRUD and connection-test endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.exceptions import (
    ActiveProfileDeletionError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from app.db.database import get_db
from app.schemas.smtp_profile import (
    SMTPConnectionStatus,
    SMTPProfileCreate,
    SMTPProfileResponse,
    SMTPProfileUpdate,
    SMTPTestRequest,
    SMTPTestResponse,
)
from app.services.smtp_service import SMTPService

router = APIRouter()


def _service(db: Session) -> SMTPService:
    return SMTPService(db)


@router.post(
    "/",
    response_model=SMTPProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create SMTP Profile",
)
async def create_smtp_profile(
    profile: SMTPProfileCreate,
    db: Session = Depends(get_db),
):
    """Add a new SMTP profile. Email, required fields, and port are validated."""
    try:
        return await _service(db).create_profile(profile)
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SMTP profile: {exc}",
        )


@router.get(
    "/",
    response_model=List[SMTPProfileResponse],
    summary="List SMTP Profiles",
)
async def list_smtp_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """List SMTP profiles with pagination. Stored passwords are never returned."""
    return await _service(db).get_profiles(
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get(
    "/active/current",
    response_model=Optional[SMTPProfileResponse],
    summary="Get Active SMTP Profile",
)
async def get_active_profile(db: Session = Depends(get_db)):
    """Return the currently active SMTP profile, or null if none is active."""
    return await _service(db).get_active_profile()


@router.get(
    "/status/all",
    response_model=List[SMTPConnectionStatus],
    summary="Get SMTP Profile Statuses",
)
async def get_all_statuses(db: Session = Depends(get_db)):
    """Return connection status summaries for all SMTP profiles."""
    return await _service(db).get_all_statuses()


@router.post(
    "/test-connection",
    response_model=SMTPTestResponse,
    summary="Test SMTP Connection",
)
async def test_smtp_connection(
    test_request: SMTPTestRequest,
    db: Session = Depends(get_db),
):
    """
    Test one SMTP profile by connecting and authenticating.

    If test_email is provided, the endpoint also sends a small test message.
    Connection failures return HTTP 200 with success=false so callers can show
    a normal validation result instead of treating it as an API crash.
    """
    try:
        return await _service(db).test_connection(
            test_request.profile_id,
            test_request.test_email,
        )
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/test-all",
    response_model=List[SMTPTestResponse],
    summary="Test All SMTP Connections",
)
async def test_all_connections(db: Session = Depends(get_db)):
    """Test every saved SMTP profile and update each connection status."""
    return await _service(db).test_all_connections()


@router.get(
    "/{profile_id}",
    response_model=SMTPProfileResponse,
    summary="Get SMTP Profile",
)
async def get_smtp_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Get one SMTP profile by ID."""
    try:
        return await _service(db).get_profile(profile_id)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put(
    "/{profile_id}",
    response_model=SMTPProfileResponse,
    summary="Update SMTP Profile",
)
async def update_smtp_profile(
    profile_id: int,
    profile_update: SMTPProfileUpdate,
    db: Session = Depends(get_db),
):
    """Update an SMTP profile. Only provided fields are changed."""
    try:
        return await _service(db).update_profile(profile_id, profile_update)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update SMTP profile: {exc}",
        )


@router.patch(
    "/{profile_id}",
    response_model=SMTPProfileResponse,
    summary="Partially Update SMTP Profile",
)
async def patch_smtp_profile(
    profile_id: int,
    profile_update: SMTPProfileUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an SMTP profile."""
    return await update_smtp_profile(profile_id, profile_update, db)


@router.delete(
    "/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete SMTP Profile",
)
async def delete_smtp_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Delete an SMTP profile. Active profiles must be deactivated first."""
    try:
        await _service(db).delete_profile(profile_id)
        return None
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ActiveProfileDeletionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/{profile_id}/set-active",
    response_model=SMTPProfileResponse,
    summary="Set Active SMTP Profile",
)
async def set_active_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """Set one SMTP profile as active and deactivate all others."""
    try:
        return await _service(db).set_active_profile(profile_id)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
