from src import app
from src.db.main import get_session
from src.auth.dependencies import RoleChecker, AccessTokenBearer, RefreshTokenBearer
import src.auth.routes as auth_routes
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock
from httpx import AsyncClient, ASGITransport
import pytest

client = TestClient(app)
async_mock_session = AsyncMock()
async_mock_user_service = AsyncMock()
async_mock_book_service = AsyncMock()


async def get_mock_session():
    yield async_mock_session


access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock()
app.dependency_overrides[access_token_bearer] = Mock()
app.dependency_overrides[refresh_token_bearer] = Mock()
auth_routes.user_service = async_mock_user_service
auth_routes.send_email = Mock()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_mocks():
    async_mock_session.reset_mock()
    async_mock_user_service.reset_mock()
    async_mock_book_service.reset_mock()
    auth_routes.send_email.reset_mock()


@pytest.fixture
async def fake_session():
    return async_mock_session


@pytest.fixture
async def fake_user_service():
    return async_mock_user_service


@pytest.fixture
async def fake_book_service():
    return async_mock_book_service


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
async def test_async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client
