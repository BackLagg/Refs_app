import uuid
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth import models
from src.auth.auth_cookie import fastapi_users
from src.auth.manager import get_user_manager, UserManager
from src.auth.models import User, Referral
from src.auth.schemas import ReferralCodeResponse, ReferralRegistrationResponse, UserCreate, UserCreateRefs, \
    ReferralResponse
from src.database import redis, get_async_session

refs_router = APIRouter()

# Получение текущего пользователя
current_user = fastapi_users.current_user()

async def generate_referral_code(user_id: int):
    # Проверяем, существует ли код у пользователя
    referral_code = await redis.get(f"referral:{user_id}")
    if referral_code:
        raise HTTPException(status_code=400, detail="У вас уже есть активный реферальный код")

    # Генерируем новый код
    code = str(uuid.uuid4())
    await redis.setex(f"referral:{user_id}", timedelta(minutes=60), code)  # Код на 24 часа
    await redis.setex(f"user_refs:{code}", timedelta(minutes=60), user_id)  # Код на 24 часа

    return code

# Эндпоинт для создания реферального кода
@refs_router.post("/add_referral_code", response_model=ReferralCodeResponse)
async def create_referral_code(
    user: User = Depends(current_user)
):
    code = await generate_referral_code(user.id)
    return ReferralCodeResponse(code=code, expires_in=3 *60* 60)

@refs_router.post("/del_referral_code")
async def delete_referral_code(
    user: User = Depends(current_user),):
    # Получаем реферальный код из Redis
    referral_code = await redis.get(f"referral:{user.id}")
    if not referral_code:
        raise HTTPException(status_code=404, detail="Реферальный код не найден")

    # Удаляем реферальный код из Redis
    await redis.delete(f"referral:{user.id}")
    await redis.delete(f"user_refs:{referral_code.decode('utf-8')}")

    return {"message": "Реферальный код успешно удален"}
# Эндпоинт для получения текущего реферального кода
@refs_router.get("/show_referral_code", response_model=ReferralCodeResponse)
async def get_referral_code(user: models.User = Depends(current_user)):
    referral_code = await redis.get(f"referral:{user.id}")
    if not referral_code:
        raise HTTPException(status_code=404, detail="Реферальный код не найден")

    ttl = await redis.ttl(f"referral:{user.id}")
    return ReferralCodeResponse(code=referral_code.decode(), expires_in=ttl)

# Эндпоинт регистрации с использованием реферального кода
@refs_router.post("/register", response_model=ReferralRegistrationResponse)
async def register_user_with_referral(
    user_data: UserCreateRefs,
    user_manager: UserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session)
):
    # Проверка реферального кода, если он указан
    referrer_id = None
    if user_data.referral_code:
        referrer_id = await redis.get(f"user_refs:{user_data.referral_code}")
        if not referrer_id:
            raise HTTPException(status_code=404, detail="Реферальный код недействителен или истек")
    print(user_data)
    # Создание пользователя
    user_create = UserCreate(
        email=user_data.email,
        password=user_data.password,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
        is_verified=user_data.is_verified,
    )
    try:
        new_user = await user_manager.create(user_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Если есть реферальный код, создаем запись связи
    if referrer_id:
        referral = Referral(user_id=int(referrer_id), referred_user_id=new_user.id)
        session.add(referral)
        await session.commit()

    return ReferralRegistrationResponse(
        message="Регистрация успешна",
        user_id=new_user.id,
    )

@refs_router.get("/my_referrals")
async def get_my_referrals(
    user: User = Depends(current_user),  # Получаем текущего пользователя
    session: AsyncSession = Depends(get_async_session)  # Получаем сессию базы данных
):
    # Получаем рефералов текущего пользователя
    query = (
        select(Referral)
        .options(selectinload(Referral.referred_user))  # Загружаем рефералов вместе с пользователями
        .where(Referral.user_id == user.id)
    )
    result = await session.execute(query)
    referrals = result.scalars().all()  # Получаем все записи из запроса

    if not referrals:
        raise HTTPException(status_code=404, detail="У вас нет рефералов")

    # Формируем ответ
    referral_data = [
        {
            "id": referral.referred_user.id,
            "email": referral.referred_user.email,
            "registration_date": referral.referred_user.reg_at,
        }
        for referral in referrals
    ]

    return referral_data


@refs_router.get("/referrals_by_id")
async def get_referrals_by_user_id(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    # Получаем рефералов для указанного user_id
    query = (
        select(Referral)
        .options(selectinload(Referral.referred_user))
        .where(Referral.user_id == user_id)
    )

    result = await session.execute(query)
    referrals = result.scalars().all()

    # Если у пользователя нет рефералов, возвращаем 404
    if not referrals:
        raise HTTPException(status_code=404, detail="Рефералы не найдены")

    # Формируем список рефералов
    referral_data = [
        {
            "id": referral.referred_user.id,
            "email": referral.referred_user.email,
            "registration_date": referral.referred_user.reg_at,
        }
        for referral in referrals
    ]

    return referral_data


@refs_router.get("/referral_code_by_email")
async def get_referral_code_by_email(
        email: str,
        session: AsyncSession = Depends(get_async_session),
):
    # Получение пользователя по email из базы данных
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получение реферального кода из Redis по user_id
    referral_code_bytes = await redis.get(f"referral:{user.id}")

    if not referral_code_bytes:
        raise HTTPException(status_code=404, detail="Реферальный код не найден")

    # Декодирование байтовой строки в строку
    referral_code = referral_code_bytes.decode('utf-8')

    return {"referral_code": referral_code}