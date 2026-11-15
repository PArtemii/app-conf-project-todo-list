import json
from unittest.mock import MagicMock, patch

import psycopg
import pytest

from main import health_check


@pytest.mark.parametrize("database_url,expected_status,expected_content", [
    ("postgresql://localhost:5432/db", 200, {"status": "healthy", "database": "ok"}),
    (None, 503, {"status": "unhealthy", "database": "DATABASE_URL is not set"}),
])
def test_health_check(database_url, expected_status, expected_content):
    """Test health_check function with different database URL scenarios."""
    with (
        patch("main.settings.database_url", database_url),
        patch("psycopg.connect") as mock_connect,
    ):
        mock_connect.return_value = MagicMock()

        response = health_check()

        if expected_status == 200:
            assert response == expected_content
        else:
            assert response.status_code == expected_status
            assert json.loads(response.body) == expected_content


# Test case for database connection error
@pytest.mark.parametrize("database_url,expected_status,expected_content", [
    ("postgresql://localhost:5432/db", 503, {"status": "unhealthy", "database": "unavailable"}),
])
def test_health_check_database_connection_error(database_url, expected_status, expected_content):
    """Test health_check when database connection fails."""
    with (
        patch("main.settings.database_url", database_url),
        patch("psycopg.connect") as mock_connect,
    ):
        mock_connect.side_effect = psycopg.Error("Database connection error")

        response = health_check()

        assert response.status_code == expected_status
        assert json.loads(response.body) == expected_content


# Test case for missing DATABASE_URL
@pytest.mark.parametrize("database_url,expected_status,expected_content", [
    (None, 503, {"status": "unhealthy", "database": "DATABASE_URL is not set"}),
])
def test_health_check_missing_database_url(database_url, expected_status, expected_content):
    """Test health_check when DATABASE_URL is not set."""
    with patch("main.settings.database_url", database_url):
        response = health_check()

        assert response.status_code == expected_status
        assert json.loads(response.body) == expected_content
