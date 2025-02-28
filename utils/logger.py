"""
Logger utility for the application.

This module provides a centralized logging system for the application,
recording important actions such as user login/logout, admin actions,
user registration, etc.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from datetime import datetime
import ipaddress
from functools import wraps
from flask import request, session

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure the logger
logger = logging.getLogger('boko_hacks')
logger.setLevel(logging.INFO)

# Create a file handler that logs to a file with rotation (max 10MB, keep 5 backup files)
log_file = os.path.join(LOGS_DIR, 'app.log')
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)

# Define log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)

def sanitize_ip(ip: str) -> str:
    """
    Sanitize IP address to protect privacy by removing the last octet.
    
    Args:
        ip: The IP address to sanitize
        
    Returns:
        Sanitized IP address with last octet replaced by 'xxx'
    """
    try:
        if ip and ip != '127.0.0.1' and ip != 'localhost':
            if ':' in ip:  # IPv6
                return str(ipaddress.IPv6Address(ip)).rsplit(':', 1)[0] + ':xxx'
            else:  # IPv4
                return '.'.join(ip.split('.')[:3]) + '.xxx'
        return ip
    except:
        return 'unknown'

def log_action(action_type: str, message: str, level: str = 'info', 
               user: Optional[str] = None, admin: bool = False, 
               extra_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an action with standardized formatting.
    
    Args:
        action_type: Type of action (login, logout, register, admin_action, etc.)
        message: Description of the action
        level: Log level (info, warning, error, critical)
        user: Username associated with the action
        admin: Whether this is an admin action
        extra_data: Any additional data to include in the log
    """
    if not user and session.get('user'):
        user = session.get('user')
    
    # Get client IP and sanitize it
    client_ip = request.remote_addr if request else 'unknown'
    sanitized_ip = sanitize_ip(client_ip)
    
    # Format the log message
    log_message = f"[{action_type.upper()}] "
    if user:
        log_message += f"User: {user} "
    if admin:
        log_message += "[ADMIN] "
    
    log_message += f"IP: {sanitized_ip} - {message}"
    
    # Add extra data if provided
    if extra_data:
        log_message += f" - Data: {extra_data}"
    
    # Log at the appropriate level
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(log_message)

def log_login(success: bool, username: str, admin: bool = False, reason: Optional[str] = None) -> None:
    """
    Log a login attempt.
    
    Args:
        success: Whether the login was successful
        username: The username that attempted to login
        admin: Whether this was an admin login
        reason: Optional reason for login failure
    """
    status = "successful" if success else "failed"
    action_type = "admin_login" if admin else "user_login"
    level = "info" if success else "warning"
    
    message = f"Login {status} for user {username}"
    if not success and reason:
        message += f" - Reason: {reason}"
    
    log_action(
        action_type=action_type,
        message=message,
        level=level,
        user=username if success else None,
        admin=admin
    )

def log_logout(username: str, admin: bool = False) -> None:
    """
    Log a logout action.
    
    Args:
        username: The username that logged out
        admin: Whether this was an admin logout
    """
    action_type = "admin_logout" if admin else "user_logout"
    
    log_action(
        action_type=action_type,
        message=f"Logout for user {username}",
        user=username,
        admin=admin
    )

def log_registration(success: bool, username: str, reason: Optional[str] = None) -> None:
    """
    Log a user registration attempt.
    
    Args:
        success: Whether the registration was successful
        username: The username that attempted to register
        reason: Reason for failure if unsuccessful
    """
    status = "successful" if success else "failed"
    level = "info" if success else "warning"
    message = f"Registration {status} for user {username}"
    
    if not success and reason:
        message += f" - Reason: {reason}"
    
    log_action(
        action_type="registration",
        message=message,
        level=level,
        user=username if success else None
    )

def log_admin_action(action: str, admin_username: str, target: Optional[str] = None, 
                    success: bool = True, details: Optional[str] = None) -> None:
    """
    Log an admin action.
    
    Args:
        action: The type of admin action (add_user, remove_admin, reset_password, etc.)
        admin_username: The admin username performing the action
        target: The target of the action (e.g., username being modified)
        success: Whether the action was successful
        details: Additional details about the action
    """
    status = "successful" if success else "failed"
    level = "info" if success else "warning"
    
    message = f"Admin action '{action}' {status}"
    if target:
        message += f" on target '{target}'"
    if details:
        message += f" - Details: {details}"
    
    log_action(
        action_type="admin_action",
        message=message,
        level=level,
        user=admin_username,
        admin=True
    )

def log_error(error_type: str, message: str, user: Optional[str] = None, 
             admin: bool = False, exception: Optional[Exception] = None) -> None:
    """
    Log an error.
    
    Args:
        error_type: Type of error
        message: Error message
        user: Username associated with the error
        admin: Whether this error occurred during an admin action
        exception: The exception object if available
    """
    error_message = message
    if exception:
        error_message += f" - Exception: {str(exception)}"
    
    log_action(
        action_type="error",
        message=error_message,
        level="error",
        user=user,
        admin=admin
    )

def log_security_event(event_type: str, message: str, severity: str = "warning",
                      user: Optional[str] = None) -> None:
    """
    Log a security-related event.
    
    Args:
        event_type: Type of security event (e.g., 'unauthorized_access', 'brute_force')
        message: Description of the security event
        severity: Severity level (info, warning, error, critical)
        user: Username associated with the event
    """
    log_action(
        action_type=f"security_{event_type}",
        message=message,
        level=severity,
        user=user
    )
