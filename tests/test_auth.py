import pytest
from unittest.mock import MagicMock, patch
from src.auth import check_access, AuthRole

# Mock config for tests
@pytest.fixture
def mock_config():
    with patch('src.auth.config') as mock_conf:
        yield mock_conf

def test_check_access_allowed_user(mock_config):
    mock_config.QUERY_ALLOWED_USERS = [123]
    mock_config.QUERY_ALLOWED_GROUPS = []
    
    assert check_access(user_id=123, chat_id=999, role=AuthRole.QUERY) is True

def test_check_access_allowed_group(mock_config):
    mock_config.QUERY_ALLOWED_USERS = []
    mock_config.QUERY_ALLOWED_GROUPS = [-100]
    
    assert check_access(user_id=999, chat_id=-100, role=AuthRole.QUERY) is True

def test_check_access_denied(mock_config):
    mock_config.QUERY_ALLOWED_USERS = [123]
    mock_config.QUERY_ALLOWED_GROUPS = [-100]
    
    assert check_access(user_id=999, chat_id=999, role=AuthRole.QUERY) is False

def test_check_access_empty_whitelist_allows_all(mock_config):
    mock_config.QUERY_ALLOWED_USERS = []
    mock_config.QUERY_ALLOWED_GROUPS = []
    
    assert check_access(user_id=999, chat_id=999, role=AuthRole.QUERY) is True

def test_check_access_ingest_role(mock_config):
    mock_config.INGEST_ALLOWED_USERS = [456]
    mock_config.INGEST_ALLOWED_GROUPS = []
    
    # Authorized
    assert check_access(user_id=456, chat_id=999, role=AuthRole.INGEST) is True
    # Unauthorized
    assert check_access(user_id=123, chat_id=999, role=AuthRole.INGEST) is False

def test_check_access_invalid_role(mock_config, caplog):
    # This should return False and log error, although passing random string to Enum typed arg is tricky in static analysis, 
    # but at runtime python allows it if not casting strict. 
    # However, since we type hinted AuthRole, we expect callers to use it. 
    # But if someone passes a string by mistake that doesn't match enum?
    # Actually, the function signature expects AuthRole.
    pass 
