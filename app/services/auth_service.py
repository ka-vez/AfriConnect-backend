"""
Authentication service - Business logic for auth operations.
"""

from sqlmodel import Session, select
from app.models import User, UserRole, Founder, Investor, StartupStage
from app.schemas.auth import SignUpRequest
from app.utils.security import hash_password, verify_password
from app.utils.jwt_handler import create_access_token
from app.utils.errors import ConflictError, AuthenticationError, ValidationError
from typing import Tuple


class AuthService:
    """
    Service class for authentication operations.
    Handles user registration and login with role-specific profiles.
    """
    
    @staticmethod
    def _validate_password(password: str) -> None:
        """
        Validate password meets requirements.
        Bcrypt has a 72-byte limit, enforce it here.
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationError: If password is invalid
        """
        if len(password) < 8:
            raise ValidationError(detail="Password must be at least 8 characters")
        
        # Check byte length (bcrypt limit is 72 bytes)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValidationError(
                detail=f"Password is too long. Maximum 72 bytes allowed, got {len(password_bytes)} bytes"
            )
    
    @staticmethod
    def signup(session: Session, signup_data: SignUpRequest) -> Tuple[User, str]:
        """
        Register a new user with their role-specific profile.
        
        Creates a User record and initializes either a Founder or Investor profile
        based on the provided role.
        
        Args:
            session: Database session
            signup_data: User signup data (email, password, role, etc.)
            
        Returns:
            Tuple of (created user, JWT access token)
            
        Raises:
            ConflictError: If email already exists
            ValidationError: If role is invalid or required fields missing
        """
        # Check if email already exists
        existing_user = session.exec(
            select(User).where(User.email == signup_data.email)
        ).first()
        
        if existing_user:
            raise ConflictError(detail="Email already registered")
        
        # Validate and normalize role
        role_lower = signup_data.role.lower().strip()
        if role_lower not in ["founder", "investor"]:
            raise ValidationError(detail="Role must be 'founder' or 'investor'")
        
        # Convert string role to UserRole enum
        user_role = UserRole.FOUNDER if role_lower == "founder" else UserRole.INVESTOR
        
        # Validate password before hashing
        AuthService._validate_password(signup_data.password)
        
        # Hash password
        password_hash = hash_password(signup_data.password)
        
        # Create new user
        user = User(
            email=signup_data.email,
            password_hash=password_hash,
            full_name=signup_data.full_name,
            role=user_role,
        )
        
        session.add(user)
        session.flush()  # Get the user ID without committing

        if user.id is None:
            raise RuntimeError("Failed to create user ID")
        user_id: int = user.id
        
        # Create role-specific profile
        if user_role == UserRole.FOUNDER:
            founder = Founder(
                user_id=user_id,
                startup_name=signup_data.startup_name or "Unnamed Startup",
                startup_pitch=signup_data.startup_pitch or "",
                startup_sector=signup_data.startup_sector or "Technology",
                the_ask=signup_data.the_ask or 100000.0,
                stage=StartupStage.IDEA,
            )
            session.add(founder)
        
        elif user_role == UserRole.INVESTOR:
            investor = Investor(
                user_id=user_id,
                firm_name=signup_data.firm_name or "Investment Firm",
                investment_thesis=signup_data.investment_thesis or "",
                min_ticket_size=signup_data.min_ticket_size or 50000.0,
                max_ticket_size=signup_data.max_ticket_size or 500000.0,
            )
            session.add(investor)
        
        # Commit everything
        session.commit()
        session.refresh(user)
        
        # Generate JWT token (expires in 30 minutes)
        access_token = create_access_token(data={"sub": str(user_id)})
        
        return user, access_token
    
    @staticmethod
    def login(session: Session, email: str, password: str) -> Tuple[User, str]:
        """
        Authenticate user and return JWT token.
        
        Validates email/password combination and checks user is active.
        
        Args:
            session: Database session
            email: User email address
            password: Plain text password
            
        Returns:
            Tuple of (authenticated user, JWT access token)
            
        Raises:
            AuthenticationError: If credentials are invalid or user inactive
        """
        # Validate password before querying
        try:
            AuthService._validate_password(password)
        except ValidationError:
            # Don't leak that password is too long - just say invalid
            raise AuthenticationError(detail="Invalid email or password")
        
        # Find user by email
        user = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        # Check if user exists
        if not user:
            raise AuthenticationError(detail="Invalid email or password")
        
        # Check password is correct
        if not verify_password(password, user.password_hash):
            raise AuthenticationError(detail="Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError(detail="User account is inactive")

        if user.id is None:
            raise AuthenticationError(detail="Invalid user account")
        
        user_id: int = user.id
        
        # Generate JWT token (expires in 30 minutes)
        access_token = create_access_token(data={"sub": str(user_id)})
        
        return user, access_token
