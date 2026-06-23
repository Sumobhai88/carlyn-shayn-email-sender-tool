"""
Custom exception classes for better error handling
"""


class AppException(Exception):
    """Base exception for application errors"""
    pass


class ProfileNotFoundError(AppException):
    """Raised when SMTP profile is not found"""
    def __init__(self, profile_id: int):
        self.profile_id = profile_id
        super().__init__(f"SMTP profile with ID {profile_id} not found")


class ProfileAlreadyExistsError(AppException):
    """Raised when trying to create profile with existing name"""
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"SMTP profile with name '{profile_name}' already exists")


class ActiveProfileDeletionError(AppException):
    """Raised when trying to delete active profile"""
    def __init__(self, profile_id: int):
        self.profile_id = profile_id
        super().__init__(
            f"Cannot delete active SMTP profile (ID: {profile_id}). "
            "Please set another profile as active first."
        )


class SMTPConnectionError(AppException):
    """Raised when SMTP connection fails"""
    def __init__(self, message: str, details: str = None):
        self.details = details
        super().__init__(message)


class CampaignNotFoundError(AppException):
    """Raised when campaign is not found"""
    def __init__(self, campaign_id: int):
        self.campaign_id = campaign_id
        super().__init__(f"Campaign with ID {campaign_id} not found")


class InvalidCSVError(AppException):
    """Raised when CSV file is invalid"""
    def __init__(self, message: str):
        super().__init__(f"Invalid CSV file: {message}")
