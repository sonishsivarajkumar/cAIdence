"""
Basic User Authentication for cAIdence.

This module provides basic user authentication capabilities including
user registration, login, session management, and role-based access control.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import secrets
import sqlite3
import bcrypt
import logging
from pathlib import Path
import jwt
from enum import Enum

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles for access control."""
    ADMIN = "admin"
    RESEARCHER = "researcher"
    CLINICIAN = "clinician"
    ANALYST = "analyst"
    VIEWER = "viewer"


@dataclass
class User:
    """Represents a user in the system."""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}


@dataclass
class UserSession:
    """Represents a user session."""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True


class AuthenticationManager:
    """Manages user authentication and sessions."""
    
    def __init__(self, db_path: str = "caidence_auth.db", secret_key: str = None):
        """Initialize authentication manager.
        
        Args:
            db_path: Path to SQLite database file
            secret_key: Secret key for JWT tokens
        """
        self.db_path = Path(db_path)
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expiry = timedelta(hours=8)  # 8-hour sessions
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    preferences TEXT
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Login attempts table for security
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    ip_address TEXT,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    user_agent TEXT
                )
            """)
            
            conn.commit()
    
    def create_user(self, username: str, email: str, full_name: str, 
                   password: str, role: UserRole = UserRole.VIEWER) -> Optional[User]:
        """Create a new user.
        
        Args:
            username: Unique username
            email: User email address
            full_name: User's full name
            password: Plain text password
            role: User role
            
        Returns:
            Created user object or None if creation failed
        """
        try:
            # Generate user ID
            user_id = self._generate_user_id(username, email)
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user = User(
                id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                is_active=True,
                created_at=datetime.now()
            )
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users 
                    (id, username, email, full_name, password_hash, role, 
                     is_active, created_at, preferences)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.id, user.username, user.email, user.full_name,
                    password_hash, user.role.value, user.is_active,
                    user.created_at.isoformat(), "{}"
                ))
                conn.commit()
            
            logger.info(f"Created user: {username} ({user_id})")
            return user
            
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed - duplicate username/email: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = "", user_agent: str = "") -> Optional[Tuple[User, str]]:
        """Authenticate a user and create session.
        
        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (User object, session token) or None if authentication failed
        """
        try:
            # Log the attempt
            self._log_login_attempt(username, ip_address, False, user_agent)
            
            # Get user from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, full_name, password_hash, role, 
                           is_active, created_at, last_login, preferences
                    FROM users 
                    WHERE (username = ? OR email = ?) AND is_active = TRUE
                """, (username, username))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Authentication failed - user not found: {username}")
                    return None
                
                # Verify password
                stored_hash = row[4]
                if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    logger.warning(f"Authentication failed - invalid password: {username}")
                    return None
                
                # Create user object
                user = User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    role=UserRole(row[5]),
                    is_active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_login=datetime.fromisoformat(row[8]) if row[8] else None,
                    preferences=eval(row[9]) if row[9] else {}
                )
                
                # Create session
                session_token = self._create_session(user, ip_address, user_agent)
                
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = ? WHERE id = ?
                """, (datetime.now().isoformat(), user.id))
                conn.commit()
                
                # Log successful attempt
                self._log_login_attempt(username, ip_address, True, user_agent)
                
                logger.info(f"User authenticated: {username} ({user.id})")
                return user, session_token
                
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate a session token and return user.
        
        Args:
            session_token: JWT session token
            
        Returns:
            User object if session is valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(session_token, self.secret_key, algorithms=['HS256'])
            session_id = payload.get('session_id')
            user_id = payload.get('user_id')
            
            if not session_id or not user_id:
                return None
            
            # Check session in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.user_id, s.expires_at, s.is_active,
                           u.username, u.email, u.full_name, u.role,
                           u.is_active, u.created_at, u.last_login, u.preferences
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.session_id = ? AND s.is_active = TRUE AND u.is_active = TRUE
                """, (session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Check expiration
                expires_at = datetime.fromisoformat(row[1])
                if datetime.now() > expires_at:
                    # Deactivate expired session
                    cursor.execute("""
                        UPDATE user_sessions SET is_active = FALSE WHERE session_id = ?
                    """, (session_id,))
                    conn.commit()
                    return None
                
                # Update last activity
                cursor.execute("""
                    UPDATE user_sessions SET last_activity = ? WHERE session_id = ?
                """, (datetime.now().isoformat(), session_id))
                conn.commit()
                
                # Create user object
                user = User(
                    id=row[0],
                    username=row[3],
                    email=row[4],
                    full_name=row[5],
                    role=UserRole(row[6]),
                    is_active=bool(row[7]),
                    created_at=datetime.fromisoformat(row[8]),
                    last_login=datetime.fromisoformat(row[9]) if row[9] else None,
                    preferences=eval(row[10]) if row[10] else {}
                )
                
                return user
                
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token provided")
            return None
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout a user by deactivating their session.
        
        Args:
            session_token: JWT session token
            
        Returns:
            True if logout successful, False otherwise
        """
        try:
            payload = jwt.decode(session_token, self.secret_key, algorithms=['HS256'])
            session_id = payload.get('session_id')
            
            if not session_id:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions SET is_active = FALSE WHERE session_id = ?
                """, (session_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return False
    
    def check_permission(self, user: User, required_role: UserRole) -> bool:
        """Check if user has required permissions.
        
        Args:
            user: User object
            required_role: Required role level
            
        Returns:
            True if user has sufficient permissions
        """
        role_hierarchy = {
            UserRole.ADMIN: 5,
            UserRole.RESEARCHER: 4,
            UserRole.CLINICIAN: 3,
            UserRole.ANALYST: 2,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def _create_session(self, user: User, ip_address: str, user_agent: str) -> str:
        """Create a new session for user.
        
        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            JWT session token
        """
        # Generate session ID
        session_id = secrets.token_urlsafe(32)
        
        # Calculate expiration
        expires_at = datetime.now() + self.token_expiry
        
        # Save session to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions 
                (session_id, user_id, created_at, expires_at, last_activity,
                 ip_address, user_agent, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user.id, datetime.now().isoformat(),
                expires_at.isoformat(), datetime.now().isoformat(),
                ip_address, user_agent, True
            ))
            conn.commit()
        
        # Create JWT token
        payload = {
            'session_id': session_id,
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'exp': expires_at,
            'iat': datetime.now()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def _generate_user_id(self, username: str, email: str) -> str:
        """Generate a unique user ID.
        
        Args:
            username: Username
            email: Email address
            
        Returns:
            Unique user identifier
        """
        content = f"{username}:{email}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _log_login_attempt(self, username: str, ip_address: str, 
                          success: bool, user_agent: str) -> None:
        """Log a login attempt for security monitoring.
        
        Args:
            username: Attempted username
            ip_address: Client IP address
            success: Whether attempt was successful
            user_agent: Client user agent
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO login_attempts 
                    (username, ip_address, timestamp, success, user_agent)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    username, ip_address, datetime.now().isoformat(),
                    success, user_agent
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging login attempt: {str(e)}")
    
    def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """Get active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active sessions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, user_id, created_at, expires_at,
                           last_activity, ip_address, user_agent, is_active
                    FROM user_sessions 
                    WHERE user_id = ? AND is_active = TRUE
                    ORDER BY last_activity DESC
                """, (user_id,))
                
                sessions = []
                for row in cursor.fetchall():
                    session = UserSession(
                        session_id=row[0],
                        user_id=row[1],
                        created_at=datetime.fromisoformat(row[2]),
                        expires_at=datetime.fromisoformat(row[3]),
                        last_activity=datetime.fromisoformat(row[4]),
                        ip_address=row[5],
                        user_agent=row[6],
                        is_active=bool(row[7])
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE expires_at < ? AND is_active = TRUE
                """, (datetime.now().isoformat(),))
                conn.commit()
                
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            return 0


def create_default_admin(auth_manager: AuthenticationManager, 
                        username: str = "admin", 
                        password: str = "caidence_admin_2025") -> Optional[User]:
    """Create a default admin user if no admin exists.
    
    Args:
        auth_manager: Authentication manager instance
        username: Admin username
        password: Admin password
        
    Returns:
        Created admin user or None if already exists
    """
    try:
        # Check if any admin exists
        with sqlite3.connect(auth_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = TRUE
            """)
            
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                # Create default admin
                admin_user = auth_manager.create_user(
                    username=username,
                    email=f"{username}@caidence.local",
                    full_name="System Administrator",
                    password=password,
                    role=UserRole.ADMIN
                )
                
                if admin_user:
                    logger.info(f"Created default admin user: {username}")
                    return admin_user
            
            return None
            
    except Exception as e:
        logger.error(f"Error creating default admin: {str(e)}")
        return None
