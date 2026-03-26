import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from src.auth.schemas import UserCreateSchema
import src.auth.routes as auth_routes

auth_prefix = "/api/v1/auth"


def make_mock_user():
    mock_user = MagicMock()
    mock_user.uid = uuid.uuid4()
    mock_user.username = "estevan_uon"
    mock_user.email = "estevan@uon.dev"
    mock_user.first_name = "Estevan"
    mock_user.last_name = "Ulian"
    mock_user.is_verified = False
    mock_user.password_hash = "hashed"
    mock_user.created_at = datetime.now(timezone.utc)
    mock_user.updated_at = datetime.now(timezone.utc)
    return mock_user


signup_data = {
    "first_name": "Estevan",
    "last_name": "Ulian",
    "email": "estevan@uon.dev",
    "username": "estevan_uon",
    "password": "teste@123"
}


@pytest.mark.anyio
async def test_user_signup(fake_session, fake_user_service, test_async_client):
    fake_user_service.user_exists.return_value = False
    fake_user_service.create_user.return_value = make_mock_user()

    response = await test_async_client.post(
        url=f"{auth_prefix}/signup",
        json=signup_data
    )

    user_data = UserCreateSchema(**signup_data)
    fake_user_service.user_exists.assert_called_once()
    fake_user_service.user_exists.assert_called_once_with(
        signup_data["email"],
        fake_session
    )
    fake_user_service.create_user.assert_called_once()
    fake_user_service.create_user.assert_called_once_with(
        user_data, fake_session)
    assert response.status_code == 201


@pytest.mark.anyio
async def test_user_signup_sends_verification_email(fake_session, fake_user_service, test_async_client):
    fake_user_service.user_exists.return_value = False
    fake_user_service.create_user.return_value = make_mock_user()
    auth_routes.send_email.reset_mock()

    await test_async_client.post(
        url=f"{auth_prefix}/signup",
        json=signup_data
    )

    auth_routes.send_email.delay.assert_called_once()


@pytest.mark.anyio
async def test_user_signup_user_already_exists(fake_session, fake_user_service, test_async_client):
    fake_user_service.user_exists.return_value = True

    response = await test_async_client.post(
        url=f"{auth_prefix}/signup",
        json=signup_data
    )

    fake_user_service.create_user.assert_not_called()
    assert response.status_code == 409
    assert response.json()["error_code"] == "USER_EXISTS"


@pytest.mark.anyio
async def test_user_signup_missing_required_field(fake_user_service, test_async_client):
    incomplete_data = {
        "first_name": "Estevan",
        "last_name": "Ulian",
        "username": "estevan_uon",
        "password": "teste@123"
        # email ausente
    }

    response = await test_async_client.post(
        url=f"{auth_prefix}/signup",
        json=incomplete_data
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["message"] == "Validation error"
    assert response.json()["errors"][0]["field"] == "email"
    assert response.json()["errors"][0]["message"] == "Field required"


@pytest.mark.anyio
async def test_user_signup_username_too_short(fake_user_service, test_async_client):
    invalid_data = {**signup_data, "username": "ab"}  # min_length=3

    response = await test_async_client.post(
        url=f"{auth_prefix}/signup",
        json=invalid_data
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_user_signup_password_too_short(fake_user_service, test_async_client):
    invalid_data = {**signup_data, "password": "123"}  # min_length=6

    response = await test_async_client.post(
        url=f"{auth_prefix}/signup",
        json=invalid_data
    )

    assert response.status_code == 422
