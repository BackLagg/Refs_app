from asyncio import get_event_loop_policy

import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app  # Замените на правильный импорт

# Создаем отдельный event loop для фикстуры сессии
@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

#фикстура с логином для каждого теста
@pytest.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_response = await client.post("/api/auth/jwt/login", data={
            "username": "user0@example.com",
            "password": "string"
        })
        cookies = {"Refs_app": login_response.cookies["Refs_app"]}
        client.cookies.update(cookies)
        yield client

#фикстура для передачи реф-кода меду тестами(для регистрации по коду)
@pytest.fixture()
async def referral_code(client):
    response = await client.get("/show_referral_code")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Details: {response.json()}"
    return response.json()["code"]