import logging
from functools import wraps
from enum import Enum
from telegram import Update
from telegram.ext import ContextTypes
from src.config import config

logger = logging.getLogger(__name__)

class AuthRole(Enum):
    QUERY = 'query'
    INGEST = 'ingest'

def check_access(user_id: int, chat_id: int, role: AuthRole) -> bool:
    """
    Checks if the user or group is allowed for the given role.
    
    If no whitelist is configured (both lists are empty), default to ALLOW.
    """
    if role == AuthRole.QUERY:
        allowed_users = config.QUERY_ALLOWED_USERS
        allowed_groups = config.QUERY_ALLOWED_GROUPS
    elif role == AuthRole.INGEST:
        allowed_users = config.INGEST_ALLOWED_USERS
        allowed_groups = config.INGEST_ALLOWED_GROUPS
    else:
        logger.error(f"Unknown role for access check: {role}")
        return False

    # If no whitelist is configured, allow all (with warning)
    if not allowed_users and not allowed_groups:
        return True

    if user_id in allowed_users:
        return True
    
    if chat_id in allowed_groups:
        return True
        
    return False

def auth_required(role: AuthRole):
    """
    Decorator to enforce whitelist access control.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            chat = update.effective_chat
            
            if not user or not chat:
                # Should not happen in standard message handlers
                return await func(update, context, *args, **kwargs)

            if not check_access(user.id, chat.id, role):
                logger.warning(f"Unauthorized access attempt: User={user.id}, Chat={chat.id}, Role={role}")
                if update.message:
                    await update.message.reply_text("⛔ אין לך הרשאה להשתמש בבוט זה.")
                return

            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
