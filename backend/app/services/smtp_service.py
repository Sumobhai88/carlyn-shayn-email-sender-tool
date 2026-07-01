"""
SMTP Profile business logic service with comprehensive validation and testing
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.models.smtp_profile import SMTPProfile
from app.schemas.smtp_profile import (
    SMTPProfileCreate,
    SMTPProfileUpdate,
    SMTPTestResponse,
    SMTPConnectionStatus
)
from app.core.exceptions import (
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
    ActiveProfileDeletionError,
)
from app.core.security import decrypt_secret, encrypt_secret

logger = logging.getLogger(__name__)


class SMTPService:
    """Service for SMTP profile management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================================================
    # CREATE
    # ==========================================================================
    
    async def create_profile(self, profile_data: SMTPProfileCreate, user_id: int = None) -> SMTPProfile:
        """Create new SMTP profile"""
        # Check unique name per user only (not globally)
        query = self.db.query(SMTPProfile).filter(SMTPProfile.profile_name == profile_data.profile_name)
        if user_id is not None:
            query = query.filter(SMTPProfile.user_id == user_id)
        if query.first():
            raise ProfileAlreadyExistsError(profile_data.profile_name)
        
        profile_dict = profile_data.model_dump()
        profile_dict['password'] = encrypt_secret(profile_data.password)
        if user_id is not None:
            profile_dict['user_id'] = user_id
        
        # Remove profile_name from dict temporarily, add manually to avoid unique constraint issues
        profile = SMTPProfile(**profile_dict)
        self.db.add(profile)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise ProfileAlreadyExistsError(profile_data.profile_name)
        self.db.refresh(profile)
        return profile
    
    # ==========================================================================
    # READ
    # ==========================================================================
    
    async def get_profiles(self, skip: int = 0, limit: int = 100, active_only: bool = False, user_id: int = None) -> List[SMTPProfile]:
        """Get SMTP profiles for current user"""
        query = self.db.query(SMTPProfile)
        if user_id is not None:
            query = query.filter(SMTPProfile.user_id == user_id)
        if active_only:
            query = query.filter(SMTPProfile.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    async def get_profile(self, profile_id: int, user_id: int = None) -> SMTPProfile:
        """Get SMTP profile by ID"""
        query = self.db.query(SMTPProfile).filter(SMTPProfile.id == profile_id)
        if user_id is not None:
            query = query.filter(SMTPProfile.user_id == user_id)
        profile = query.first()
        if not profile:
            raise ProfileNotFoundError(profile_id)
        return profile
    
    async def get_active_profile(self, user_id: int = None) -> Optional[SMTPProfile]:
        """Get currently active SMTP profile for user"""
        query = self.db.query(SMTPProfile).filter(SMTPProfile.is_active == True)
        if user_id is not None:
            query = query.filter(SMTPProfile.user_id == user_id)
        return query.first()
    
    # ==========================================================================
    # UPDATE
    # ==========================================================================
    
    async def update_profile(self, profile_id: int, profile_update: SMTPProfileUpdate, user_id: int = None) -> SMTPProfile:
        """Update SMTP profile"""
        profile = await self.get_profile(profile_id, user_id=user_id)
        
        # Update only provided fields
        update_data = profile_update.model_dump(exclude_unset=True)
        
        # Check for duplicate name if updating
        if 'profile_name' in update_data:
            existing = self.db.query(SMTPProfile).filter(
                SMTPProfile.profile_name == update_data['profile_name'],
                SMTPProfile.id != profile_id
            ).first()
            
            if existing:
                raise ProfileAlreadyExistsError(update_data['profile_name'])
        
        activate_profile = update_data.pop('is_active', None)

        # Apply updates
        for field, value in update_data.items():
            # Encode password if updating
            if field == 'password':
                value = encrypt_secret(value)
            setattr(profile, field, value)

        if activate_profile is True:
            self.db.query(SMTPProfile).filter(
                SMTPProfile.id != profile_id
            ).update({"is_active": False})
            profile.is_active = True
        elif activate_profile is False:
            profile.is_active = False
        
        self.db.commit()
        self.db.refresh(profile)
        
        logger.info(f"Updated SMTP profile: {profile.profile_name} (ID: {profile.id})")
        return profile
    
    # ==========================================================================
    # DELETE
    # ==========================================================================
    
    async def delete_profile(self, profile_id: int, user_id: int = None):
        """Delete SMTP profile"""
        profile = await self.get_profile(profile_id, user_id=user_id)
        if profile.is_active:
            raise ActiveProfileDeletionError(profile_id)
        self.db.delete(profile)
        self.db.commit()
    
    async def set_active_profile(self, profile_id: int, user_id: int = None) -> SMTPProfile:
        """Set SMTP profile as active - deactivates all others for this user"""
        profile = await self.get_profile(profile_id, user_id=user_id)
        # Only deactivate this user's profiles
        query = self.db.query(SMTPProfile)
        if user_id is not None:
            query = query.filter(SMTPProfile.user_id == user_id)
        query.update({"is_active": False})
        profile.is_active = True
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    # ==========================================================================
    # CONNECTION TESTING
    # ==========================================================================
    
    async def test_connection(
        self,
        profile_id: int,
        test_email: Optional[str] = None
    ) -> SMTPTestResponse:
        """
        Test SMTP connection and optionally send test email
        
        Process:
        1. Retrieve profile
        2. Attempt SMTP connection
        3. Authenticate
        4. Send test email (if email provided)
        5. Update profile status
        
        Args:
            profile_id: Profile ID to test
            test_email: Optional email to send test to
            
        Returns:
            Test result with success status and details
        """
        profile = await self.get_profile(profile_id)
        
        try:
            logger.info(f"Testing SMTP connection for: {profile.profile_name}")
            
            profile.status = "testing"
            self.db.commit()

            use_tls = profile.tls_enabled and profile.smtp_port == 465
            start_tls = profile.tls_enabled and not use_tls

            # Create SMTP connection. Port 465 uses implicit TLS; ports such as
            # 587 connect first and upgrade with STARTTLS.
            smtp = aiosmtplib.SMTP(
                hostname=profile.smtp_host,
                port=profile.smtp_port,
                use_tls=use_tls,
                start_tls=start_tls,
                timeout=30.0
            )
            
            # Connect
            await smtp.connect()
            logger.debug(f"Connected to {profile.smtp_host}:{profile.smtp_port}")
            
            # Authenticate
            smtp_password = decrypt_secret(profile.password)
            await smtp.login(profile.username, smtp_password)
            logger.debug(f"Authenticated as {profile.username}")
            
            # Send test email if requested
            if test_email:
                message = MIMEMultipart("alternative")
                message["Subject"] = "SMTP Test Email - Carlyn Shayn Email Engine"
                message["From"] = f"{profile.sender_name} <{profile.sender_email}>"
                message["To"] = test_email
                
                # Create email body
                text_body = f"""
SMTP Connection Test Successful!

Profile: {profile.profile_name}
SMTP Host: {profile.smtp_host}
SMTP Port: {profile.smtp_port}
Sender: {profile.sender_name} <{profile.sender_email}>

This is an automated test email from Carlyn Shayn Email Engine.
If you received this, your SMTP configuration is working correctly!

---
Carlyn Shayn Email Engine
Email Automation Platform
                """.strip()
                
                message.attach(MIMEText(text_body, "plain"))
                
                await smtp.send_message(message)
                logger.info(f"Test email sent to {test_email}")
            
            # Close connection
            await smtp.quit()
            
            # Update profile status
            profile.status = "connected"
            self.db.commit()
            
            result_message = "Connection successful"
            if test_email:
                result_message += f" and test email sent to {test_email}"
            
            logger.info(f"SMTP test successful: {profile.profile_name}")
            
            return SMTPTestResponse(
                success=True,
                message=result_message,
                status="connected",
                profile_id=profile_id,
                test_email=test_email,
                error_details=None
            )
        
        except aiosmtplib.SMTPAuthenticationError as e:
            error_msg = "Authentication failed - check username and password"
            logger.error(f"SMTP auth failed for {profile.profile_name}: {str(e)}")
            profile.status = "failed"
            self.db.commit()
            
            return SMTPTestResponse(
                success=False,
                message=error_msg,
                status="failed",
                profile_id=profile_id,
                test_email=test_email,
                error_details=str(e)
            )
        
        except aiosmtplib.SMTPConnectError as e:
            error_msg = f"Connection failed - check host and port"
            logger.error(f"SMTP connection failed for {profile.profile_name}: {str(e)}")
            profile.status = "failed"
            self.db.commit()
            
            return SMTPTestResponse(
                success=False,
                message=error_msg,
                status="failed",
                profile_id=profile_id,
                test_email=test_email,
                error_details=str(e)
            )
        
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            logger.error(f"SMTP test error for {profile.profile_name}: {str(e)}")
            profile.status = "failed"
            self.db.commit()
            
            return SMTPTestResponse(
                success=False,
                message=error_msg,
                status="failed",
                profile_id=profile_id,
                test_email=test_email,
                error_details=str(e)
            )
    
    # ==========================================================================
    # BULK OPERATIONS
    # ==========================================================================
    
    async def get_all_statuses(self, user_id: int = None) -> List[SMTPConnectionStatus]:
        """Get connection status for all profiles of current user"""
        profiles = await self.get_profiles(user_id=user_id)
        return [
            SMTPConnectionStatus(id=p.id, profile_name=p.profile_name, status=p.status, is_active=p.is_active, last_tested=p.updated_at)
            for p in profiles
        ]
    
    async def test_all_connections(self, user_id: int = None) -> List[SMTPTestResponse]:
        """Test all SMTP connections for current user"""
        profiles = await self.get_profiles(user_id=user_id)
        results = []
        for profile in profiles:
            try:
                result = await self.test_connection(profile.id)
                results.append(result)
            except Exception as e:
                results.append(SMTPTestResponse(success=False, message=f"Test failed: {str(e)}", status="failed", profile_id=profile.id, error_details=str(e)))
        return results
