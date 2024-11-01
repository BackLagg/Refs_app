import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app

#Некоторые тесты могут не пройти не из-за ошибок, а из-за того что данные уже есть в бд
#Поменяйте входные данные чтоб проходить тесты регистраций

#тест регистрации
@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Регистрация пользователя
        reg_response = await client.post("/api/auth/register", json={
            "email": "user0@example.com", #вставить любые данные
            "password": "string",
            "is_active": True,
            "is_superuser": True,
            "is_verified": False
        })
        assert reg_response.status_code == 201, f"Registration failed, got {reg_response.status_code}. Details: {reg_response.json()}"

#тест проверки авторизации
@pytest.mark.asyncio
async def test_router_check(client):
    response = await client.get("/api/auth/check")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"

#тест создания реф-кода
@pytest.mark.asyncio
async def test_router_add_ref(client):
    response = await client.post("/add_referral_code")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"

#тест просмотра своего реф-кода
@pytest.mark.asyncio
async def test_router_show_ref(client):
    response = await client.get("/show_referral_code")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"

#тест регистрации с кодом(реф код передаётся с помощью фикстуры)
@pytest.mark.asyncio
async def test_reg_with_code(referral_code):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Регистрация пользователя
        login_response = await client.post("/register", json={
            "email": "user1@example.com", #поменять данные при необходимости
            "password": "string",
            "is_active": True,
            "is_superuser": True,
            "is_verified": False,
            "referral_code": referral_code
        })
        assert login_response.status_code == 201, f"Registration failed, got {login_response.status_code}. Details: {repr(login_response.json())}"

#тест просмотра своих рефералов
@pytest.mark.asyncio
async def test_router_my_referrals(client):
    response = await client.get("/my_referrals")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"

#тест просмотра рефералов по id
@pytest.mark.asyncio
async def test_router_referrals_by_id(client):
    # Замените 1 на актуальный ID, который существует в вашей базе данных для теста
    referral_id = 1
    response = await client.post("/referrals_by_id", json={"id": referral_id})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"

#тест просмотра реф-кода по email
@pytest.mark.asyncio
async def test_router_referral_code_by_email(client):
    # Замените на актуальный email, который существует в вашей базе данных для теста
    email = "user@example.com"
    response = await client.post("/referral_code_by_email", json={"email": email})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"

#тест удаления своего реф-кода
@pytest.mark.asyncio
async def test_router_del_ref(client):
    response = await client.post("/del_referral_code")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"
